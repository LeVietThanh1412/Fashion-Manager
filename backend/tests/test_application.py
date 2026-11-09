from datetime import datetime
import asyncio
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from mysql.connector import IntegrityError
from pydantic import ValidationError

from app.db.academic_queries import load_academic_queries
import app.repositories.employees as employee_repository
from app.documents import document_base
from app.permissions import store_scope
from app.schemas import Assignment, Order
from main import app, mysql_error_handler

ROOT = Path(__file__).resolve().parents[2]


def order(**changes):
    data = dict(ma_don_hang='TEST',ma_nhan_vien='NV024',ma_khach_hang='KH001',ngay_tao_don=datetime(2026,10,25,10),chi_tiet=[dict(ma_san_pham='SP001',so_luong=1)])
    data.update(changes)
    return data


@pytest.mark.parametrize('quantity',[0,-1,1.5,'2',True])
def test_order_rejects_non_positive_or_non_integer_quantities(quantity):
    with pytest.raises(ValidationError):
        Order(**order(chi_tiet=[dict(ma_san_pham='SP001',so_luong=quantity)]))


def test_order_requires_lines_and_unique_products():
    with pytest.raises(ValidationError):
        Order(**order(chi_tiet=[]))
    with pytest.raises(ValidationError):
        Order(**order(chi_tiet=[dict(ma_san_pham='SP001',so_luong=1)]*2))


def test_zero_price_is_valid_but_negative_is_not():
    assert Order(**order(chi_tiet=[dict(ma_san_pham='SP001',so_luong=1,don_gia_ban=0)])).chi_tiet[0].don_gia_ban == 0
    with pytest.raises(ValidationError):
        Order(**order(chi_tiet=[dict(ma_san_pham='SP001',so_luong=1,don_gia_ban=-1)]))



def test_health_and_missing_employee_do_not_require_database():
    with TestClient(app) as client:
        assert client.get('/health').status_code == 200
        assert client.post('/api/orders', json={
            'customer_id': 'KH001',
            'details': [{'product_id': 'SP001', 'quantity': 1}],
        }).status_code == 401
        assert client.get('/').status_code == 200


@pytest.mark.parametrize(('errno', 'message', 'path', 'status_code', 'detail'), [
    (1062, "Duplicate entry 'NV001' for key 'nhan_vien.ma_nhan_vien'", '/api/employees',
     409, 'Mã nhân viên đã tồn tại. Hãy kiểm tra hoặc nhập mã nhân viên khác.'),
    (1062, "Duplicate entry '0900000000' for key 'nhan_vien.so_dien_thoai'", '/api/employees',
     409, 'Số điện thoại đã tồn tại. Hãy kiểm tra hoặc nhập số điện thoại khác.'),
    (1452, "Cannot add or update: CONSTRAINT `fk_nv_manager` FOREIGN KEY (`ma_quan_ly`)",
     '/api/employees', 400, 'Mã quản lý trực tiếp không tồn tại. Hãy chọn lại mã quản lý trực tiếp.'),
    (3819, "Check constraint 'ck_nhan_vien_luong' is violated.", '/api/employees',
         400, 'Lương không hợp lệ. Hãy nhập mức lương lớn hơn 0.'),
])
def test_mysql_constraint_errors_name_the_field_and_rule(errno, message, path, status_code, detail):
    error = IntegrityError(msg=message, errno=errno)
    request = SimpleNamespace(url=SimpleNamespace(path=path))

    response = asyncio.run(mysql_error_handler(request, error))

    assert response.status_code == status_code
    assert json.loads(response.body) == {'detail': detail}


def test_distribution_documents_use_the_store_recorded_on_the_distribution():
    base, *_ = document_base('distributions')

    assert 'JOIN cua_hang ch ON ch.ma_cua_hang=d.ma_cua_hang' in base


def test_queries_have_at_least_fifty_distinct_ids_and_statements():
    registry=load_academic_queries(ROOT/'sql'/'query')
    assert len(registry)>=50
    assert len({query.sql for query in registry.values()})==len(registry)
    for member in range(1,6):
        assert sum(key.startswith(f'M{member:02}_') for key in registry)>=10


def test_no_redundant_current_price_or_detail_identifier_in_schema():
    sql=(ROOT/'sql'/'data'/'01_create_database.sql').read_text(encoding='utf-8')
    assert '    gia_ban ' not in sql
    assert 'ma_chi_tiet' not in sql
    assert 'UNIQUE (ma_don_hang,ma_san_pham)' not in sql

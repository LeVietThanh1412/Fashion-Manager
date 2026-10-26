from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.db.academic_queries import load_academic_queries
from app.permissions import store_scope
from app.schemas import Assignment, Order
from main import app

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


@pytest.mark.parametrize('data',[
    dict(quyen_han='admin',ma_cua_hang='CH001'),
    dict(quyen_han='staff'),
    dict(quyen_han='regional_manager'),
    dict(quyen_han='store_manager',ma_cua_hang='CH001',khu_vuc_quan_ly=1),
])
def test_assignment_rejects_inconsistent_scope(data):
    with pytest.raises(ValidationError):
        Assignment(**data)


@pytest.mark.parametrize('actor,expected',[
    ({'quyen_han':'admin'},('1=1',[])),
    ({'quyen_han':'regional_manager','khu_vuc_quan_ly':2},('ch.khu_vuc = %s',[2])),
    ({'quyen_han':'staff','ma_cua_hang':'CH001'},('ch.ma_cua_hang = %s',['CH001'])),
])
def test_role_scope(actor,expected):
    assert store_scope(actor) == expected


def test_health_and_missing_employee_do_not_require_database():
    with TestClient(app) as client:
        assert client.get('/health').status_code == 200
        assert client.post('/api/orders', json={
            'customer_id': 'KH001',
            'details': [{'product_id': 'SP001', 'quantity': 1}],
        }).status_code == 401
        assert client.get('/').status_code == 200


def test_queries_have_at_least_fifty_distinct_ids_and_statements():
    registry=load_academic_queries(ROOT/'sql'/'query')
    assert len(registry)>=50
    assert len({query.sql for query in registry.values()})==len(registry)
    for member in range(1,6):
        assert sum(key.startswith(f'M{member:02}_') for key in registry)>=10


def test_no_redundant_current_price_or_detail_identifier_in_schema():
    sql=(ROOT/'sql'/'1.TaoCoSoDuLieu.sql').read_text(encoding='utf-8')
    assert '    gia_ban ' not in sql
    assert 'ma_chi_tiet' not in sql
    assert 'UNIQUE (ma_don_hang,ma_san_pham)' not in sql

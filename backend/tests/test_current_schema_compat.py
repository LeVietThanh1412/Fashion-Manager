from contextlib import contextmanager
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.core.roles import role_from_database, role_to_database
from app.db.academic_queries import AcademicQuery, adapt_query_to_current_schema
from app.repositories import auth, catalog, employees, orders, sales
from app.schemas.employees import EmployeeInput, SalaryInput


def patched_connection(monkeypatch, repository, cursor):
    connection = MagicMock()
    connection.cursor.return_value = cursor

    @contextmanager
    def connected():
        yield connection

    monkeypatch.setattr(repository, "connection", connected)
    return connection


def test_database_roles_map_to_application_roles():
    assert role_from_database("quan_ly") == "admin"
    assert role_from_database("quan_ly_khu_vuc") == "regional_manager"
    assert role_from_database("quan_ly_cua_hang") == "store_manager"
    assert role_from_database("nhan_vien") == "staff"
    assert role_to_database("staff") == "nhan_vien"


def test_employee_salary_matches_current_database_constraint():
    employee = EmployeeInput(
        employee_id="NV999",
        name="Nhan Vien Moi",
        phone="0900000999",
        email="new@example.test",
        role="staff",
        store_id="CH001",
        salary=1,
    )

    assert employee.salary == 1
    with pytest.raises(ValidationError):
        SalaryInput(salary=0)
    with pytest.raises(ValidationError):
        EmployeeInput(**{**employee.model_dump(), "salary": 1.5})


def test_auth_query_adapts_role_and_synthesizes_unsupported_status(monkeypatch):
    cursor = MagicMock()
    cursor.fetchone.return_value = {
        "ma_nhan_vien": "NV000",
        "quyen_han": "quan_ly",
        "trang_thai": "active",
    }
    patched_connection(monkeypatch, auth, cursor)

    user = auth.get_user_by_phone("0900000000")

    assert user["quyen_han"] == "admin"
    assert user["trang_thai"] == "active"
    sql = cursor.execute.call_args.args[0]
    assert "'active' AS trang_thai" in sql
    assert "nv.trang_thai" not in sql


def test_product_query_uses_database_price_column_with_existing_api_alias(monkeypatch):
    cursor = MagicMock()
    cursor.fetchall.return_value = []
    patched_connection(monkeypatch, catalog, cursor)

    catalog.list_products(None, None, 20, 0)

    sql = cursor.execute.call_args.args[0]
    assert "gia_san_pham AS gia_ban" in sql
    assert "gia_ban," not in sql


def test_distribution_uses_employee_store_relation(monkeypatch):
    cursor = MagicMock()
    cursor.fetchall.return_value = []
    patched_connection(monkeypatch, employees, cursor)

    employees.get_distribution("CH001")

    sql = cursor.execute.call_args.args[0]
    assert "JOIN nhan_vien AS nv ON nv.ma_nhan_vien = pp.ma_nhan_vien" in sql
    assert "pp.ma_cua_hang" not in sql


def test_order_inserts_only_columns_available_in_current_schema(monkeypatch):
    cursor = MagicMock()
    cursor.fetchone.side_effect = [("KH001",), ("SP001",)]
    connection = patched_connection(monkeypatch, orders, cursor)

    order_id = orders.create_order(
        "NV001",
        "KH001",
        [{"product_id": "SP001", "quantity": 2}],
    )

    assert order_id.startswith("DH")
    statements = [call.args[0] for call in cursor.execute.call_args_list]
    detail_insert = next(sql for sql in statements if "INSERT INTO chi_tiet_don_hang" in sql)
    assert "(ma_don_hang, ma_san_pham, so_luong)" in detail_insert
    assert "don_gia_ban" not in detail_insert
    connection.commit.assert_called_once()


def test_sales_queries_calculate_revenue_from_current_product_price():
    assert "sp.gia_san_pham" in sales._DAILY_SQL
    assert "sp.gia_san_pham" in sales._RECENT_ORDERS_SQL
    assert "don_gia_ban" not in sales._DAILY_SQL + sales._RECENT_ORDERS_SQL


def test_academic_revenue_query_uses_current_product_price_without_editing_source():
    query = AcademicQuery(
        "M04_Q01",
        "Don hang va doanh thu 1",
        "SELECT SUM(ct.so_luong*ct.don_gia_ban) AS doanh_thu "
        "FROM don_hang d JOIN chi_tiet_don_hang ct "
        "ON ct.ma_don_hang=d.ma_don_hang;",
    )

    statement, notice = adapt_query_to_current_schema(query)

    assert "sp.gia_san_pham" in statement
    assert "JOIN san_pham sp ON sp.ma_san_pham = ct.ma_san_pham" in statement
    assert query.sql != statement
    assert notice is not None


def test_academic_detail_queries_use_columns_present_in_current_schema():
    query = AcademicQuery(
        "M05_Q10",
        "Bao cao tong hop 10",
        "SELECT COUNT(ct.ma_chi_tiet) FROM chi_tiet_don_hang ct;",
    )

    statement, notice = adapt_query_to_current_schema(query)

    assert "ct.ma_san_pham" in statement
    assert "ma_chi_tiet" not in statement
    assert notice is None

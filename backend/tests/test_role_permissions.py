from dataclasses import replace
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

import app.core.authentication as authentication
import app.routers.auth as auth_router
import app.routers.employees as employee_router
import app.routers.orders as order_router
from app.core.config import settings
from app.core.security import create_access_token, decode_access_token
import app.core.security as security
from main import app


def user(role, employee_id="NV100", store_id="CH01", region_id=1, store_region=1):
    return {
        "ma_nhan_vien": employee_id,
        "ho_ten": "Test User",
        "so_dien_thoai": "0900000000",
        "quyen_han": role,
        "ma_cua_hang": store_id,
        "khu_vuc_quan_ly": region_id if role == "regional_manager" else None,
        "store_region": store_region,
        "trang_thai": "active",
    }


def override_user(actor):
    app.dependency_overrides[authentication.get_current_user] = lambda: actor


def clear_overrides():
    app.dependency_overrides.clear()


def test_staff_can_create_order_but_store_manager_cannot(monkeypatch):
    create_order = MagicMock(return_value="DH123")
    monkeypatch.setattr(order_router, "create_order", create_order)
    payload = {
        "customer_id": "KH01",
        "employee_id": "NV000",
        "details": [{"product_id": "SP01", "quantity": 2}],
    }

    override_user(user("store_manager"))
    with TestClient(app) as client:
        assert client.post("/api/orders", json=payload).status_code == 403
    create_order.assert_not_called()

    override_user(user("staff", employee_id="NV200"))
    with TestClient(app) as client:
        response = client.post("/api/orders", json=payload)
    assert response.status_code == 201
    assert response.json()["order_id"] == "DH123"
    assert create_order.call_args.args[0] == "NV200"
    clear_overrides()


def test_employee_salary_scope_and_hierarchy_are_enforced(monkeypatch):
    manager = user("store_manager")
    same_store_staff = {
        **user("staff", employee_id="NV201", store_id="CH01"),
        "store_region": 1,
    }
    other_store_staff = {
        **user("staff", employee_id="NV202", store_id="CH02"),
        "store_region": 1,
    }
    update_salary = MagicMock(return_value=True)
    monkeypatch.setattr(employee_router, "get_employee", lambda employee_id: {
        "NV201": same_store_staff,
        "NV202": other_store_staff,
    }.get(employee_id))
    monkeypatch.setattr(employee_router, "update_salary", update_salary)
    override_user(manager)

    with TestClient(app) as client:
        allowed = client.put("/api/employees/NV201/salary", json={"salary": 25000000})
        denied = client.put("/api/employees/NV202/salary", json={"salary": 25000000})
    assert allowed.status_code == 200
    assert denied.status_code == 403
    assert update_salary.call_count == 1
    clear_overrides()


def test_regional_manager_cannot_create_admin_or_cross_region_employee(monkeypatch):
    regional = user("regional_manager", store_id=None, region_id=1)
    monkeypatch.setattr(employee_router, "store_region", lambda _store: 2)
    override_user(regional)
    payload = {
        "employee_id": "NV300",
        "name": "New staff",
        "phone": "0900000001",
        "email": "new@example.test",
        "role": "staff",
        "store_id": "CH02",
    }
    with TestClient(app) as client:
        cross_region = client.post("/api/employees", json=payload)
        admin_role = client.post("/api/employees", json={**payload, "role": "admin"})
    assert cross_region.status_code == 403
    assert admin_role.status_code == 422
    clear_overrides()


def test_staff_cannot_read_employee_management_or_sales(monkeypatch):
    override_user(user("staff"))
    with TestClient(app) as client:
        assert client.get("/api/employees").status_code == 403
        assert client.get("/api/analytics/sales").status_code == 403
    clear_overrides()


def test_staff_distribution_is_scoped_to_signed_in_store(monkeypatch):
    distribution = MagicMock(return_value=[{"ma_san_pham": "SP01", "so_luong_phan_phoi": 4}])
    monkeypatch.setattr(employee_router, "get_distribution", distribution)
    override_user(user("staff", store_id="CH09"))
    with TestClient(app) as client:
        response = client.get("/api/employee/distribution")
    assert response.status_code == 200
    assert response.json()["quantity_type"] == "distributed"
    distribution.assert_called_once_with("CH09")
    clear_overrides()


def test_signed_token(monkeypatch):
    monkeypatch.setattr(
        security,
        "settings",
        replace(settings, auth_token_secret="test-secret-value-that-is-at-least-32-bytes"),
    )
    token, _ = create_access_token("NV000")
    assert decode_access_token(token)["employee_id"] == "NV000"


def test_login_uses_employee_id_as_password(monkeypatch):
    monkeypatch.setattr(
        security,
        "settings",
        replace(settings, auth_token_secret="test-secret-value-that-is-at-least-32-bytes"),
    )
    account = {
        **user("staff", employee_id="NV401"),
        "so_dien_thoai": "0900000041",
    }
    monkeypatch.setattr(auth_router, "get_user_by_phone", lambda _phone: account)
    monkeypatch.setattr(authentication, "get_user_by_id", lambda _employee_id: account)

    with TestClient(app) as client:
        wrong_password = client.post(
            "/api/auth/login",
            json={"phone": "0900000041", "password": "wrong"},
        )
        login_response = client.post(
            "/api/auth/login",
            json={"phone": "0900000041", "password": "NV401"},
        )
        assert wrong_password.status_code == 401
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "must_change_password" not in login_data["user"]
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {login_data['access_token']}"},
        )
    assert me_response.status_code == 200
    assert me_response.json()["user"]["employee_id"] == "NV401"

def test_employee_manager_sql_contains_scope_constraints():
    from pathlib import Path

    root = Path(__file__).parents[2] / "sql" / "app" / "employees"
    salary_sql = (root / "update_salary.sql").read_text(encoding="utf-8")
    assert "actor_region" in salary_sql
    assert "actor_store" in salary_sql
    assert "quyen_han <> 'admin'" in salary_sql

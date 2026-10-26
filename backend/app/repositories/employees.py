from pathlib import Path
from typing import Any

from app.core.roles import role_from_database, role_to_database
from app.db.connection import connection
from app.db.query_loader import QueryLoader

SQL_ROOT = Path(__file__).resolve().parents[3] / "sql" / "app"
loader = QueryLoader(SQL_ROOT)


def _scope(actor: dict[str, Any]) -> dict[str, Any]:
    return {
        "actor_role": actor["quyen_han"],
        "actor_region": actor["khu_vuc_quan_ly"],
        "actor_store": actor["ma_cua_hang"],
    }


def list_employees(actor: dict[str, Any]) -> list[dict[str, Any]]:
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT nv.ma_nhan_vien, nv.ho_ten, nv.so_dien_thoai, nv.email,
                       nv.quyen_han, nv.khu_vuc_quan_ly, nv.ma_cua_hang,
                       nv.luong, 'active' AS trang_thai, ch.ten_cua_hang,
                       ch.khu_vuc AS store_region
                FROM nhan_vien AS nv
                LEFT JOIN cua_hang AS ch ON ch.ma_cua_hang = nv.ma_cua_hang
                WHERE (
                    %(actor_role)s = 'admin'
                    OR (%(actor_role)s = 'regional_manager' AND ch.khu_vuc = %(actor_region)s)
                    OR (%(actor_role)s = 'store_manager'
                        AND nv.ma_cua_hang = %(actor_store)s
                        AND nv.quyen_han = 'nhan_vien')
                )
                ORDER BY nv.ho_ten, nv.ma_nhan_vien
                """,
                _scope(actor),
            )
            return [_application_employee(row) for row in cursor.fetchall()]
        finally:
            cursor.close()


def get_employee(employee_id: str) -> dict[str, Any] | None:
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT nv.ma_nhan_vien, nv.ho_ten, nv.so_dien_thoai, nv.email,
                       nv.quyen_han, nv.khu_vuc_quan_ly, nv.ma_cua_hang,
                       nv.luong, 'active' AS trang_thai, ch.khu_vuc AS store_region
                FROM nhan_vien AS nv
                LEFT JOIN cua_hang AS ch ON ch.ma_cua_hang = nv.ma_cua_hang
                WHERE nv.ma_nhan_vien = %(employee_id)s
                LIMIT 1
                """,
                {"employee_id": employee_id},
            )
            row = cursor.fetchone()
            return _application_employee(row) if row else None
        finally:
            cursor.close()


def list_stores(actor: dict[str, Any]) -> list[dict[str, Any]]:
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(loader.load("employees/list_stores.sql"), _scope(actor))
            return list(cursor.fetchall())
        finally:
            cursor.close()


def store_region(store_id: str) -> int | None:
    with connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(loader.load("employees/store_region.sql"), {"store_id": store_id})
            row = cursor.fetchone()
            return int(row[0]) if row else None
        finally:
            cursor.close()


def create_employee(employee: dict[str, Any], manager_id: str) -> None:
    with connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO nhan_vien (
                    ma_nhan_vien, ho_ten, so_dien_thoai, email, ma_cua_hang,
                    ma_quan_ly, quyen_han, khu_vuc_quan_ly, luong
                )
                VALUES (
                    %(employee_id)s, %(name)s, %(phone)s, %(email)s, %(store_id)s,
                    %(manager_id)s, %(role)s, %(region_id)s, %(salary)s
                )
                """,
                {
                    **employee,
                    "manager_id": manager_id,
                    "role": role_to_database(employee["role"]),
                    "salary": employee["salary"],
                },
            )
            conn.commit()
        finally:
            cursor.close()


def update_salary(employee_id: str, salary: Any, actor: dict[str, Any]) -> bool:
    parameters = {
        "employee_id": employee_id,
        "salary": salary,
        **_scope(actor),
    }
    with connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE nhan_vien
                SET luong = %(salary)s
                WHERE ma_nhan_vien = %(employee_id)s
                  AND (
                      (%(actor_role)s = 'admin' AND quyen_han <> 'quan_ly')
                      OR (%(actor_role)s = 'regional_manager'
                          AND quyen_han IN ('quan_ly_cua_hang', 'nhan_vien')
                          AND EXISTS (
                              SELECT 1
                              FROM cua_hang AS ch
                              WHERE ch.ma_cua_hang = nhan_vien.ma_cua_hang
                                AND ch.khu_vuc = %(actor_region)s
                          ))
                      OR (%(actor_role)s = 'store_manager'
                          AND quyen_han = 'nhan_vien'
                          AND ma_cua_hang = %(actor_store)s)
                  )
                """,
                parameters,
            )
            changed = cursor.rowcount == 1
            if changed:
                conn.commit()
            return changed
        finally:
            cursor.close()


def demote_role(employee_id: str, store_id: str | None, actor: dict[str, Any]) -> bool:
    parameters = {
        "employee_id": employee_id,
        "store_id": store_id,
        **_scope(actor),
    }
    with connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE nhan_vien
                SET quyen_han = 'nhan_vien',
                    khu_vuc_quan_ly = NULL,
                    ma_cua_hang = COALESCE(%(store_id)s, ma_cua_hang)
                WHERE ma_nhan_vien = %(employee_id)s
                  AND quyen_han IN ('quan_ly_khu_vuc', 'quan_ly_cua_hang')
                  AND (
                      %(actor_role)s = 'admin'
                      OR (%(actor_role)s = 'regional_manager'
                          AND quyen_han = 'quan_ly_cua_hang'
                          AND EXISTS (
                              SELECT 1
                              FROM cua_hang AS ch
                              WHERE ch.ma_cua_hang = nhan_vien.ma_cua_hang
                                AND ch.khu_vuc = %(actor_region)s
                          ))
                  )
                """,
                parameters,
            )
            changed = cursor.rowcount == 1
            if changed:
                conn.commit()
            return changed
        finally:
            cursor.close()


def set_employee_status(_employee_id: str, _new_status: str, _actor: dict[str, Any]) -> bool:
    return False


def get_distribution(store_id: str) -> list[dict[str, Any]]:
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT sp.ma_san_pham, sp.ten_san_pham, sp.mau_sac, sp.kich_co,
                       COALESCE(SUM(ctpp.so_luong), 0) AS so_luong_phan_phoi
                FROM san_pham AS sp
                JOIN chi_tiet_phan_phoi AS ctpp ON ctpp.ma_san_pham = sp.ma_san_pham
                JOIN phan_phoi AS pp ON pp.ma_phan_phoi = ctpp.ma_phan_phoi
                JOIN nhan_vien AS nv ON nv.ma_nhan_vien = pp.ma_nhan_vien
                WHERE nv.ma_cua_hang = %(store_id)s
                GROUP BY sp.ma_san_pham, sp.ten_san_pham, sp.mau_sac, sp.kich_co
                ORDER BY sp.ten_san_pham, sp.ma_san_pham
                """,
                {"store_id": store_id},
            )
            return list(cursor.fetchall())
        finally:
            cursor.close()


def _application_employee(row: dict[str, Any]) -> dict[str, Any]:
    employee = dict(row)
    employee["quyen_han"] = role_from_database(employee["quyen_han"])
    return employee

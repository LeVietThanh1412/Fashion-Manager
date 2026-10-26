from typing import Any

from app.core.roles import role_from_database
from app.db.connection import connection


def get_user_by_phone(phone: str) -> dict[str, Any] | None:
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT nv.ma_nhan_vien, nv.ho_ten, nv.so_dien_thoai,
                       nv.quyen_han, nv.khu_vuc_quan_ly, nv.ma_cua_hang,
                       'active' AS trang_thai, ch.khu_vuc AS store_region
                FROM nhan_vien AS nv
                LEFT JOIN cua_hang AS ch ON ch.ma_cua_hang = nv.ma_cua_hang
                WHERE nv.so_dien_thoai = %(phone)s
                LIMIT 1
                """,
                {"phone": phone},
            )
            row = cursor.fetchone()
            return _application_user(row) if row else None
        finally:
            cursor.close()


def get_user_by_id(employee_id: str) -> dict[str, Any] | None:
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT nv.ma_nhan_vien, nv.ho_ten, nv.so_dien_thoai,
                       nv.quyen_han, nv.khu_vuc_quan_ly, nv.ma_cua_hang,
                       'active' AS trang_thai, ch.khu_vuc AS store_region
                FROM nhan_vien AS nv
                LEFT JOIN cua_hang AS ch ON ch.ma_cua_hang = nv.ma_cua_hang
                WHERE nv.ma_nhan_vien = %(employee_id)s
                LIMIT 1
                """,
                {"employee_id": employee_id},
            )
            row = cursor.fetchone()
            return _application_user(row) if row else None
        finally:
            cursor.close()


def _application_user(row: dict[str, Any]) -> dict[str, Any]:
    user = dict(row)
    user["quyen_han"] = role_from_database(user["quyen_han"])
    return user

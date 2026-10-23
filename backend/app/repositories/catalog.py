from pathlib import Path
from typing import Any

from app.db.connection import connection
from app.db.query_loader import QueryLoader

SQL_ROOT = Path(__file__).resolve().parents[3] / "sql" / "app"
loader = QueryLoader(SQL_ROOT)

def list_products(search: str | None, category_id: str | None, limit: int, offset: int) -> list[dict[str, Any]]:
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                loader.load("products/list.sql"),
                {"search": search, "category_id": category_id, "limit": limit, "offset": offset},
            )
            return list(cursor.fetchall())
        finally:
            cursor.close()


def list_stores() -> list[dict[str, Any]]:
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(loader.load("stores/list.sql"))
            return list(cursor.fetchall())
        finally:
            cursor.close()


def list_categories() -> list[dict[str, Any]]:
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT dm.ma_danh_muc, dm.ten_danh_muc, COUNT(sp.ma_san_pham) AS so_san_pham
                FROM danh_muc AS dm
                LEFT JOIN san_pham AS sp ON sp.ma_danh_muc = dm.ma_danh_muc
                GROUP BY dm.ma_danh_muc, dm.ten_danh_muc
                ORDER BY dm.ten_danh_muc, dm.ma_danh_muc
                """
            )
            return list(cursor.fetchall())
        finally:
            cursor.close()


def get_catalog_summary() -> dict[str, int]:
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM san_pham) AS total_products,
                    (SELECT COUNT(*) FROM danh_muc) AS total_categories,
                    (SELECT COUNT(*) FROM cua_hang) AS total_stores,
                    (SELECT COUNT(*) FROM don_hang) AS total_orders
                """
            )
            row = cursor.fetchone()
            return {
                "total_products": int(row["total_products"]),
                "total_categories": int(row["total_categories"]),
                "total_stores": int(row["total_stores"]),
                "total_orders": int(row["total_orders"]),
            }
        finally:
            cursor.close()

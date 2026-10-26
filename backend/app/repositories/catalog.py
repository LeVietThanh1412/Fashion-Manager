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
                """
                SELECT ma_san_pham, ma_danh_muc, ten_san_pham, mau_sac, kich_co,
                       gia_san_pham AS gia_ban
                FROM san_pham
                WHERE (%(search)s IS NULL OR ten_san_pham LIKE CONCAT('%', %(search)s, '%'))
                  AND (%(category_id)s IS NULL OR ma_danh_muc = %(category_id)s)
                ORDER BY ten_san_pham, ma_san_pham
                LIMIT %(limit)s OFFSET %(offset)s
                """,
                {"search": search, "category_id": category_id, "limit": limit, "offset": offset},
            )
            return list(cursor.fetchall())
        finally:
            cursor.close()


def list_stores(actor: dict[str, Any]) -> list[dict[str, Any]]:
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                loader.load("stores/list.sql"),
                {
                    "actor_role": actor["quyen_han"],
                    "actor_region": actor["khu_vuc_quan_ly"],
                    "actor_store": actor["ma_cua_hang"],
                },
            )
            return list(cursor.fetchall())
        finally:
            cursor.close()


def list_categories() -> list[dict[str, Any]]:
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(loader.load("categories/list.sql"))
            return list(cursor.fetchall())
        finally:
            cursor.close()


def list_customers_for_orders() -> list[dict[str, Any]]:
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(loader.load("customers/list_for_order.sql"))
            return list(cursor.fetchall())
        finally:
            cursor.close()


def get_catalog_summary(actor: dict[str, Any]) -> dict[str, int]:
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                loader.load("analytics/summary.sql"),
                {
                    "actor_role": actor["quyen_han"],
                    "actor_region": actor["khu_vuc_quan_ly"],
                    "actor_store": actor["ma_cua_hang"],
                },
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

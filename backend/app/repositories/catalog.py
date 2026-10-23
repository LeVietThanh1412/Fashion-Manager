from pathlib import Path
from typing import Any

from app.db.connection import connection
from app.db.query_loader import QueryLoader

SQL_ROOT = Path(__file__).resolve().parents[3] / "sql" / "app"
loader = QueryLoader(SQL_ROOT)

_DEMO_PRODUCTS = [
    {"ma_san_pham": "SP001", "ten_san_pham": "Áo khoác Denim", "mau_sac": "Xanh", "kich_co": "M", "gia_ban": 490000, "ma_danh_muc": "DM01"},
    {"ma_san_pham": "SP002", "ten_san_pham": "Áo khoác Denim", "mau_sac": "Đen", "kich_co": "L", "gia_ban": 490000, "ma_danh_muc": "DM01"},
    {"ma_san_pham": "SP003", "ten_san_pham": "Quần jeans Slim", "mau_sac": "Xanh", "kich_co": "S", "gia_ban": 390000, "ma_danh_muc": "DM02"},
    {"ma_san_pham": "SP004", "ten_san_pham": "Quần jeans Slim", "mau_sac": "Đen", "kich_co": "M", "gia_ban": 390000, "ma_danh_muc": "DM02"},
    {"ma_san_pham": "SP005", "ten_san_pham": "Váy midi hoa", "mau_sac": "Hồng", "kich_co": "M", "gia_ban": 420000, "ma_danh_muc": "DM03"},
    {"ma_san_pham": "SP006", "ten_san_pham": "Áo thun cotton", "mau_sac": "Trắng", "kich_co": "L", "gia_ban": 220000, "ma_danh_muc": "DM04"},
    {"ma_san_pham": "SP007", "ten_san_pham": "Áo thun cotton", "mau_sac": "Đen", "kich_co": "XL", "gia_ban": 220000, "ma_danh_muc": "DM04"},
]

_DEMO_STORES = [
    {"ma_cua_hang": "CH01", "ten_cua_hang": "Fashion Avenue HCM", "dia_chi": "Q1, TP.HCM", "so_dien_thoai": "0280000001", "email": "hcm@fashion.local"},
    {"ma_cua_hang": "CH02", "ten_cua_hang": "Style Hub Hà Nội", "dia_chi": "Hai Bà Trưng, Hà Nội", "so_dien_thoai": "0240000002", "email": "hanoi@fashion.local"},
]

_DEMO_CATEGORIES = [
    {"ma_danh_muc": "DM01", "ten_danh_muc": "Áo khoác thu đông", "slug": "ao-khoac-thu-dong", "so_san_pham": 12},
    {"ma_danh_muc": "DM02", "ten_danh_muc": "Bộ sưu tập mới", "slug": "bo-suu-tap-moi", "so_san_pham": 8},
    {"ma_danh_muc": "DM03", "ten_danh_muc": "Áo sơ mi & kiểu", "slug": "ao-so-mi", "so_san_pham": 15},
    {"ma_danh_muc": "DM04", "ten_danh_muc": "Quần dài", "slug": "quan-dai", "so_san_pham": 10},
]


def list_products(search: str | None, category_id: str | None, limit: int, offset: int) -> list[dict[str, Any]]:
    try:
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
    except Exception:
        filtered = _DEMO_PRODUCTS
        if search:
            filtered = [item for item in filtered if search.lower() in item["ten_san_pham"].lower()]
        if category_id:
            filtered = [item for item in filtered if item["ma_danh_muc"] == category_id]
        return filtered[offset:offset + limit]


def list_stores() -> list[dict[str, Any]]:
    try:
        with connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(loader.load("stores/list.sql"))
                return list(cursor.fetchall())
            finally:
                cursor.close()
    except Exception:
        return _DEMO_STORES


def list_categories() -> list[dict[str, Any]]:
    try:
        with connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute("SELECT ma_danh_muc, ten_danh_muc FROM DANHMUC")
                rows = list(cursor.fetchall())
                return rows
            finally:
                cursor.close()
    except Exception:
        return _DEMO_CATEGORIES

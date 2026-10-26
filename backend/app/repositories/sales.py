from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any

from app.db.connection import connection
from app.db.query_loader import QueryLoader

VIETNAM = timezone(timedelta(hours=7))
SQL_ROOT = Path(__file__).resolve().parents[3] / "sql" / "app"
loader = QueryLoader(SQL_ROOT)

_SCOPE_SQL = """
  AND (
      %(actor_role)s = 'admin'
      OR (%(actor_role)s = 'regional_manager' AND ch.khu_vuc = %(actor_region)s)
      OR (%(actor_role)s = 'store_manager' AND ch.ma_cua_hang = %(actor_store)s)
  )
"""

_DAILY_SQL = """
SELECT DATE(dh.ngay_tao_don) AS day,
       COUNT(DISTINCT dh.ma_don_hang) AS count,
       COALESCE(SUM(ct.so_luong * sp.gia_san_pham), 0) AS revenue
FROM don_hang AS dh
JOIN nhan_vien AS nv ON nv.ma_nhan_vien = dh.ma_nhan_vien
JOIN cua_hang AS ch ON ch.ma_cua_hang = nv.ma_cua_hang
LEFT JOIN chi_tiet_don_hang AS ct ON ct.ma_don_hang = dh.ma_don_hang
LEFT JOIN san_pham AS sp ON sp.ma_san_pham = ct.ma_san_pham
WHERE dh.ngay_tao_don >= %(start)s AND dh.ngay_tao_don < %(end)s
""" + _SCOPE_SQL + """
GROUP BY DATE(dh.ngay_tao_don)
"""

_HOURLY_SQL = """
SELECT HOUR(dh.ngay_tao_don) AS hour, COUNT(DISTINCT dh.ma_don_hang) AS count
FROM don_hang AS dh
JOIN nhan_vien AS nv ON nv.ma_nhan_vien = dh.ma_nhan_vien
JOIN cua_hang AS ch ON ch.ma_cua_hang = nv.ma_cua_hang
WHERE dh.ngay_tao_don >= %(start)s AND dh.ngay_tao_don < %(end)s
""" + _SCOPE_SQL + """
GROUP BY HOUR(dh.ngay_tao_don)
"""

_RECENT_ORDERS_SQL = """
SELECT dh.ma_don_hang, dh.ngay_tao_don, dh.ma_khach_hang,
       ch.ten_cua_hang, COALESCE(ct.quantity, 0) AS quantity,
       COALESCE(ct.revenue, 0) AS revenue
FROM don_hang AS dh
JOIN nhan_vien AS nv ON nv.ma_nhan_vien = dh.ma_nhan_vien
JOIN cua_hang AS ch ON ch.ma_cua_hang = nv.ma_cua_hang
LEFT JOIN (
    SELECT ct.ma_don_hang,
           SUM(ct.so_luong) AS quantity,
           SUM(ct.so_luong * sp.gia_san_pham) AS revenue
    FROM chi_tiet_don_hang AS ct
    JOIN san_pham AS sp ON sp.ma_san_pham = ct.ma_san_pham
    GROUP BY ct.ma_don_hang
) AS ct ON ct.ma_don_hang = dh.ma_don_hang
WHERE (
    %(actor_role)s = 'admin'
    OR (%(actor_role)s = 'regional_manager' AND ch.khu_vuc = %(actor_region)s)
    OR (%(actor_role)s = 'store_manager' AND ch.ma_cua_hang = %(actor_store)s)
)
ORDER BY dh.ngay_tao_don DESC, dh.ma_don_hang DESC
LIMIT 50
"""


def get_sales_dashboard(actor: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
    today = (now or datetime.now(timezone.utc)).astimezone(VIETNAM).date()
    first = today - timedelta(days=29)
    start = datetime.combine(first, time.min)
    end = datetime.combine(today + timedelta(days=1), time.min)
    scope = {
        "actor_role": actor["quyen_han"],
        "actor_region": actor["khu_vuc_quan_ly"],
        "actor_store": actor["ma_cua_hang"],
    }
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(_DAILY_SQL, {"start": start, "end": end, **scope})
            days = {str(row["day"]): row for row in cursor.fetchall()}
            cursor.execute(_HOURLY_SQL, {"start": start, "end": end, **scope})
            hours = {int(row["hour"]): int(row["count"]) for row in cursor.fetchall()}
            cursor.execute(loader.load("analytics/sales_categories.sql"))
            categories = [
                {"id": row["id"], "name": row["name"], "count": int(row["count"])}
                for row in cursor.fetchall()
            ]
            cursor.execute(_RECENT_ORDERS_SQL, scope)
            orders = [
                {
                    "id": row["ma_don_hang"],
                    "timestamp": row["ngay_tao_don"].replace(tzinfo=VIETNAM).isoformat(),
                    "customer_id": row["ma_khach_hang"],
                    "store": row["ten_cua_hang"],
                    "quantity": int(row["quantity"]),
                    "total": int(row["revenue"]),
                }
                for row in cursor.fetchall()
            ]
        finally:
            cursor.close()

    daily = []
    for index in range(30):
        day = (first + timedelta(days=index)).isoformat()
        row = days.get(day, {})
        daily.append({
            "date": day,
            "count": int(row.get("count", 0)),
            "revenue": int(row.get("revenue", 0)),
        })
    return {
        "timezone": "Asia/Ho_Chi_Minh",
        "total_orders": sum(row["count"] for row in daily),
        "total_revenue": sum(row["revenue"] for row in daily),
        "daily": daily,
        "hourly": [{"hour": hour, "count": hours.get(hour, 0)} for hour in range(24)],
        "categories": categories,
        "orders": orders,
    }

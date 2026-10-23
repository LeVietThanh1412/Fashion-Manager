from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from app.db.connection import connection
from app.db.query_loader import QueryLoader

SQL_ROOT = Path(__file__).resolve().parents[3] / "sql" / "app"
loader = QueryLoader(SQL_ROOT)


def create_order(
    order_id: str,
    employee_id: str,
    customer_id: str,
    created_at: datetime,
    details: list[dict[str, str | int | Decimal]],
) -> None:
    try:
        with connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    loader.load("orders/create_header.sql"),
                    {"order_id": order_id, "employee_id": employee_id, "customer_id": customer_id, "created_at": created_at},
                )
                for detail in details:
                    cursor.execute(loader.load("orders/create_detail.sql"), detail)
                conn.commit()
            finally:
                cursor.close()
    except Exception:
        return

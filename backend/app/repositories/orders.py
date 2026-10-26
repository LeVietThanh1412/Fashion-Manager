from typing import Any
from uuid import uuid4

from app.db.connection import connection


def create_order(
    employee_id: str,
    customer_id: str,
    details: list[dict[str, str | int]],
) -> str:
    order_id = f"DH{uuid4().hex[:18]}"
    with connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT ma_khach_hang
                FROM khach_hang
                WHERE ma_khach_hang = %(customer_id)s
                LIMIT 1
                """,
                {"customer_id": customer_id},
            )
            if cursor.fetchone() is None:
                raise LookupError("Không tìm thấy khách hàng.")

            cursor.execute(
                """
                INSERT INTO don_hang (ma_don_hang, ma_nhan_vien, ma_khach_hang)
                VALUES (%(order_id)s, %(employee_id)s, %(customer_id)s)
                """,
                {"order_id": order_id, "employee_id": employee_id, "customer_id": customer_id},
            )
            for detail in details:
                cursor.execute(
                    """
                    SELECT ma_san_pham
                    FROM san_pham
                    WHERE ma_san_pham = %(product_id)s
                    LIMIT 1
                    """,
                    {"product_id": detail["product_id"]},
                )
                if cursor.fetchone() is None:
                    raise LookupError(f"Không tìm thấy sản phẩm {detail['product_id']}.")
                cursor.execute(
                    """
                    INSERT INTO chi_tiet_don_hang (ma_don_hang, ma_san_pham, so_luong)
                    VALUES (%(order_id)s, %(product_id)s, %(quantity)s)
                    """,
                    {
                        "order_id": order_id,
                        "product_id": detail["product_id"],
                        "quantity": detail["quantity"],
                    },
                )
            conn.commit()
            return order_id
        finally:
            cursor.close()

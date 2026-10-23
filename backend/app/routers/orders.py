from fastapi import APIRouter, status

from app.repositories.orders import create_order
from app.schemas.orders import OrderInput

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_order_endpoint(payload: OrderInput) -> dict[str, str]:
    create_order(
        payload.order_id,
        payload.employee_id,
        payload.customer_id,
        payload.created_at,
        [
            {
                "detail_id": detail.detail_id,
                "order_id": payload.order_id,
                "product_id": detail.product_id,
                "quantity": detail.quantity,
                "unit_price": detail.unit_price,
            }
            for detail in payload.details
        ],
    )
    return {"order_id": payload.order_id, "status": "created"}

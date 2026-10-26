from fastapi import APIRouter, Depends, HTTPException, status

from app.core.authentication import require_roles
from app.repositories.orders import create_order
from app.schemas.orders import OrderInput

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_order_endpoint(
    payload: OrderInput,
    employee: dict = Depends(require_roles("staff")),
) -> dict[str, str]:
    if len({detail.product_id for detail in payload.details}) != len(payload.details):
        raise HTTPException(status_code=422, detail="Mỗi sản phẩm chỉ được xuất hiện một lần trong đơn.")
    try:
        order_id = create_order(
            employee["ma_nhan_vien"],
            payload.customer_id,
            [{"product_id": detail.product_id, "quantity": detail.quantity} for detail in payload.details],
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"order_id": order_id, "status": "created"}

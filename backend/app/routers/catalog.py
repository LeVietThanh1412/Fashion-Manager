from fastapi import APIRouter, Depends, Query
from typing import Literal
from pydantic import BaseModel,Field
from app.db.helpers import transaction
from app.permissions import require_permission

from app.core.authentication import require_permissions
from app.repositories.catalog import (
    get_catalog_summary,
    list_categories,
    list_customers_for_orders,
    list_products,
    list_stores,
    list_regions,
)

router = APIRouter(prefix="/api", tags=["catalog"])


@router.get("/products")
def products(
    search: str | None = Query(default=None, max_length=100),
    category_id: str | None = Query(default=None, max_length=20),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    actor: dict = Depends(require_permissions('catalog.read')),
) -> dict[str, object]:
    items = list_products(search, category_id, limit, offset)
    return {"items": items, "page": (offset // limit) + 1, "page_size": limit}


@router.get("/stores")
def stores(permission: Literal["stores.read","sales.create","employees.write"] = "stores.read", actor: dict = Depends(require_permissions("stores.read"))) -> dict[str, object]:
    require_permission(actor,permission)
    return {"items": list_stores(actor,permission)}


@router.get("/categories")
def categories(actor: dict = Depends(require_permissions('catalog.read'))) -> dict[str, object]:
    return {"items": list_categories()}


@router.get("/customers")
def customers_for_orders(actor: dict = Depends(require_permissions("customers.read"))) -> dict[str, object]:
    return {"items": list_customers_for_orders(actor)}


@router.get("/analytics/summary")
def analytics_summary(actor: dict = Depends(require_permissions("reports.read"))) -> dict[str, object]:
    summary = get_catalog_summary(actor)
    return {
        **summary,
        "sync_status": "ok",
    }


@router.get("/regions")
def regions(actor: dict = Depends(require_permissions("stores.read"))):
    return {"items":list_regions(actor)}


class CustomerInput(BaseModel):
    customer_id: str=Field(min_length=1,max_length=20)
    name: str=Field(min_length=1,max_length=255)
    phone: str=Field(min_length=1,max_length=25)


@router.post('/customers',status_code=201)
def create_customer(payload: CustomerInput,actor=Depends(require_permissions('customers.write'))):
    with transaction() as cursor:
        cursor.execute('INSERT INTO khach_hang VALUES (%s,%s,%s)',[payload.customer_id,payload.name,payload.phone])
    return {'customer_id':payload.customer_id}

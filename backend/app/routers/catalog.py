from fastapi import APIRouter, Depends, Query

from app.core.authentication import require_roles
from app.repositories.catalog import (
    get_catalog_summary,
    list_categories,
    list_customers_for_orders,
    list_products,
    list_stores,
)

router = APIRouter(prefix="/api", tags=["catalog"])


@router.get("/products")
def products(
    search: str | None = Query(default=None, max_length=100),
    category_id: str | None = Query(default=None, max_length=20),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict[str, object]:
    items = list_products(search, category_id, limit, offset)
    return {"items": items, "page": (offset // limit) + 1, "page_size": limit}


@router.get("/stores")
def stores(actor: dict = Depends(require_roles("admin", "regional_manager", "store_manager"))) -> dict[str, object]:
    return {"items": list_stores(actor)}


@router.get("/categories")
def categories() -> dict[str, object]:
    return {"items": list_categories()}


@router.get("/customers")
def customers_for_orders(actor: dict = Depends(require_roles("staff"))) -> dict[str, object]:
    return {"items": list_customers_for_orders()}


@router.get("/analytics/summary")
def analytics_summary(actor: dict = Depends(require_roles("admin", "regional_manager", "store_manager"))) -> dict[str, object]:
    summary = get_catalog_summary(actor)
    return {
        **summary,
        "sync_status": "ok",
    }

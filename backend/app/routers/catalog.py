from fastapi import APIRouter, Query

from app.repositories.catalog import get_catalog_summary, list_products, list_stores, list_categories

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
def stores() -> dict[str, object]:
    return {"items": list_stores()}


@router.get("/categories")
def categories() -> dict[str, object]:
    return {"items": list_categories()}


@router.get("/analytics/summary")
def analytics_summary() -> dict[str, object]:
    summary = get_catalog_summary()
    return {
        **summary,
        "sync_status": "ok",
    }

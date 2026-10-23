from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.config import settings
from app.db.connection import connection
from app.routers.catalog import router as catalog_router
from app.routers.orders import router as orders_router
from app.routers.query_explorer import router as query_explorer_router

app = FastAPI(title="Fashion Manager API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app_cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(catalog_router)
app.include_router(orders_router)
app.include_router(query_explorer_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/health/db")
def database_health() -> dict[str, str]:
    try:
        with connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT VERSION()")
                version = str(cursor.fetchone()[0])
            finally:
                cursor.close()
        return {"status": "ok", "mysql_version": version}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Không thể kết nối MySQL: {exc}",
        ) from exc


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)

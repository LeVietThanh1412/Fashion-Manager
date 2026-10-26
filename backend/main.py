from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mysql.connector import Error as MySQLError
import uvicorn

from app.core.config import settings
from app.db.connection import connection
from app.db.query_loader import QueryLoader
from app.routers.catalog import router as catalog_router
from app.routers.analytics import router as analytics_router
from app.routers.auth import router as auth_router
from app.routers.employees import router as employees_router
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
app.include_router(analytics_router)
app.include_router(auth_router)
app.include_router(employees_router)
app.include_router(orders_router)
app.include_router(query_explorer_router)
SQL_LOADER = QueryLoader(Path(__file__).resolve().parents[1] / "sql" / "app")


@app.exception_handler(MySQLError)
async def mysql_error_handler(request, exc):
    return JSONResponse(
        status_code=503,
        content={"detail": "Không thể đọc/ghi MySQL. Kiểm tra kết nối, quyền truy cập và schema database."},
    )


@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def api_index() -> dict[str, str]:
    return {"service": "Fashion Manager API", "docs": "/docs", "health": "/health", "database_health": "/api/health/db"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/health/db")
def database_health() -> dict[str, str]:
    try:
        with connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(SQL_LOADER.load("health/mysql_version.sql"))
                version = str(cursor.fetchone()[0])
            finally:
                cursor.close()
        return {"status": "ok", "mysql_version": version}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Không thể kết nối MySQL. Kiểm tra DB_HOST, DB_PORT, tài khoản và TLS trên backend.",
        ) from exc


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)

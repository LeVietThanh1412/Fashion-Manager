import logging
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mysql.connector import Error as MySQLError, IntegrityError
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
from app.routers.inventory import router as inventory_router
from app.routers.access import router as access_router
from app.routers.reports import router as reports_router

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
app.include_router(inventory_router)
app.include_router(access_router)
app.include_router(reports_router)
SQL_LOADER = QueryLoader(Path(__file__).resolve().parents[1] / "sql" / "app")
logger = logging.getLogger(__name__)

DATABASE_FIELD_NAMES = {
    "ma_nhan_vien": "mã nhân viên",
    "employee_id": "mã nhân viên",
    "so_dien_thoai": "số điện thoại",
    "phone": "số điện thoại",
    "email": "email",
    "ho_ten": "họ tên",
    "name": "họ tên",
    "ma_cua_hang": "mã cửa hàng",
    "store_id": "mã cửa hàng",
    "position_id": "chức vụ",
    "ma_quan_ly": "mã quản lý trực tiếp",
    "manager_id": "mã quản lý trực tiếp",
    "khu_vuc_quan_ly": "khu vực quản lý",
    "region_id": "khu vực quản lý",
    "luong": "lương",
    "salary": "lương",
    "ma_khach_hang": "mã khách hàng",
    "customer_id": "mã khách hàng",
    "ma_san_pham": "mã sản phẩm",
    "product_id": "mã sản phẩm",
    "ma_danh_muc": "mã danh mục",
    "category_id": "mã danh mục",
    "ten_danh_muc": "tên danh mục",
    "ten_san_pham": "tên sản phẩm",
    "ten_cua_hang": "tên cửa hàng",
    "ma_don_hang": "mã đơn hàng",
    "order_id": "mã đơn hàng",
    "ma_phan_phoi": "mã phiếu phân phối",
    "distribution_id": "mã phiếu phân phối",
    "kich_co": "kích cỡ",
    "mau_sac": "màu sắc",
    "gia_san_pham": "giá sản phẩm",
    "don_gia_ban": "đơn giá bán",
    "so_luong": "số lượng",
    "quyen_han": "vai trò",
    "trang_thai": "trạng thái",
    "uq_san_pham_variant": "tên sản phẩm, màu sắc và kích cỡ",
    "ma_chuc_vu": "chức vụ",
    "ma_tai_khoan": "mã tài khoản",
}


def _database_field_name(value: str) -> str | None:
    return DATABASE_FIELD_NAMES.get(value.rsplit(".", 1)[-1].strip("`'"))


def _request_identifier_field(request) -> str:
    path = request.url.path
    for endpoint, field in (
        ("/employees", "mã nhân viên"),
        ("/customers", "mã khách hàng"),
        ("/products", "mã sản phẩm"),
        ("/categories", "mã danh mục"),
        ("/stores", "mã cửa hàng"),
        ("/orders", "mã đơn hàng"),
        ("/distributions", "mã phiếu phân phối"),
    ):
        if path.startswith(f"/api{endpoint}"):
            return field
    return "mã bản ghi"


def _integrity_error_detail(request, exc: IntegrityError) -> str:
    message = str(getattr(exc, "msg", "") or exc)
    if exc.errno == 1048:
        match = re.search(r"Column '([^']+)' cannot be null", message, re.IGNORECASE)
        field = _database_field_name(match.group(1)) if match else None
        return f"Trường {field} là bắt buộc. Hãy nhập {field}." if field else "Thiếu trường dữ liệu bắt buộc."

    if exc.errno == 1062:
        match = re.search(r"for key ['`](.+?)['`]", message, re.IGNORECASE)
        field = _database_field_name(match.group(1)) if match else None
        field = field or _request_identifier_field(request)
        return f"{field.capitalize()} đã tồn tại. Hãy kiểm tra hoặc nhập {field} khác."

    if exc.errno == 1451:
        if request.url.path.startswith("/api/employees/"):
            return "Không thể đuổi việc vì nhân viên vẫn được cấp dưới, đơn hàng hoặc phiếu phân phối tham chiếu."
        return f"Không thể xóa {_request_identifier_field(request)} vì dữ liệu khác vẫn đang tham chiếu đến bản ghi này."

    if exc.errno == 1452:
        constraints = {
            "fk_nv_manager": "mã quản lý trực tiếp",
            "fk_pclv_position": "chức vụ",
            "fk_pclv_store": "mã cửa hàng",
            "fk_pclv_warehouse": "mã kho",
            "fk_pcq_role": "vai trò",
            "fk_pcq_account": "mã tài khoản",
            "fk_dh_employee": "mã nhân viên lập đơn",
            "fk_dh_customer": "mã khách hàng",
            "fk_pp_employee": "mã nhân viên điều chuyển",
            "fk_pp_store": "mã cửa hàng nhận điều chuyển",
            "fk_mau_category": "mã danh mục",
        }
        field = next((name for constraint, name in constraints.items() if constraint in message), None)
        if not field:
            match = re.search(r"FOREIGN KEY \(`?([^` )]+)", message, re.IGNORECASE)
            field = _database_field_name(match.group(1)) if match else None
        return (
            f"{field.capitalize()} không tồn tại. Hãy chọn lại {field}."
            if field else f"Mã tham chiếu cho {_request_identifier_field(request)} không tồn tại. Hãy chọn lại dữ liệu liên quan."
        )

    if exc.errno in (3819, 4025):
        checks = (
            ("ck_pcq_scope", "Phạm vi quyền cần đúng một hệ thống, khu vực, cửa hàng hoặc kho."),
            ("ck_nv_phone", "Số điện thoại nhân viên phải ở dạng +84 và là số di động hợp lệ."),
            ("ck_nhan_vien_luong", "Lương không hợp lệ. Hãy nhập mức lương lớn hơn 0."),
            ("ck_san_pham_gia", "Giá sản phẩm không hợp lệ. Hãy nhập giá từ 0 trở lên."),
            ("ck_ctdh_so_luong", "Số lượng trong đơn hàng phải lớn hơn 0."),
            ("ck_ctpp_so_luong", "Số lượng phân phối phải lớn hơn 0."),
            ("ck_ctdh_don_gia", "Đơn giá bán không hợp lệ. Hãy nhập đơn giá từ 0 trở lên."),
        )
        for constraint, detail in checks:
            if constraint in message:
                return detail
        return f"Dữ liệu vi phạm điều kiện hợp lệ của {_request_identifier_field(request)}. Hãy kiểm tra giá trị và phạm vi được phép."

    return f"Dữ liệu không hợp lệ tại {_request_identifier_field(request)}. Hãy kiểm tra các trường bắt buộc và mã tham chiếu."


@app.exception_handler(MySQLError)
async def mysql_error_handler(request, exc):
    if isinstance(exc, IntegrityError):
        status_code = 409 if exc.errno in (1062, 1451) else 400
        return JSONResponse(
            status_code=status_code,
            content={"detail": _integrity_error_detail(request, exc)},
        )
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
def database_health() -> dict[str, str | int]:
    try:
        with connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(SQL_LOADER.load("health/mysql_version.sql"))
                version = str(cursor.fetchone()[0])
                cursor.execute('SELECT version FROM schema_version')
                schema_versions=[row[0] for row in cursor.fetchall()]
                if schema_versions != [3]:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Phiên bản schema database không tương thích. Cần schema phiên bản 3.",
                    )
            finally:
                cursor.close()
        return {"status": "ok", "mysql_version": version, "schema_version": 3}
    except MySQLError as exc:
        logger.error(
            "Database health check failed (mysql_errno=%s, error_type=%s)",
            getattr(exc, "errno", None),
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Không thể kết nối MySQL. Kiểm tra DB_HOST, DB_PORT, tài khoản và TLS trên backend.",
        ) from exc


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)

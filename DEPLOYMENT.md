# Chạy và deploy Fashion Manager

Luồng ứng dụng và bảng ánh xạ màn hình/API: [INTEGRATION.md](INTEGRATION.md).
Các bước dưới đây mô tả cấu hình từ source hiện tại; không khẳng định trạng thái deploy của
một tài khoản GitHub/Render. Thư mục bàn giao hiện không có `.git`.

## 1. Chạy local

Dùng Python 3.12/3.13. Trên máy hiện tại có Python 3.13:

```powershell
py -3.13 -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Điền cấu hình MySQL trong `.env` bằng thông tin kết nối của dịch vụ đang dùng:

```dotenv
DB_HOST=<mysql-host>
DB_PORT=<mysql-port>
DB_NAME=quan_ly_chuoi_thoi_trang
DB_USER=<mysql-user>
DB_PASSWORD=<mysql-password>
AUTH_TOKEN_SECRET=<private-random-secret-at-least-32-bytes>
APP_CORS_ORIGINS=http://127.0.0.1:8080,http://localhost:8080
# DB_SSL_CA=C:/path/to/ca.pem
```

Tạo khóa riêng bằng `py -3.13 -c "import secrets; print(secrets.token_urlsafe(48))"` rồi dán
vào `AUTH_TOKEN_SECRET`. Cấu hình local hiện đã được bổ sung khóa. Backend đọc `.env` ở gốc,
ưu tiên biến môi trường của tiến trình nếu cùng tên. `DB_SSL_CA` bật xác minh chứng chỉ và
hostname; kết nối MySQL từ xa luôn được kiểm tra có TLS.

```powershell
py -3.13 scripts/verify_db.py
py -3.13 scripts/dev.py
```

Mở http://127.0.0.1:8080. API docs: http://127.0.0.1:8000/docs.
Đăng nhập tài khoản admin trong database hiện tại bằng điện thoại `0912000000`, mật khẩu `NV000`.
Script chờ API sẵn sàng, phục vụ config local trong bộ nhớ, không thay file config deploy,
và dừng cả hai server khi Ctrl+C. Khi đổi cổng:

```powershell
py -3.13 scripts/dev.py --api-port 8010 --frontend-port 8081
```

URL giao diện khi đó là http://127.0.0.1:8081. CORS và config tự dùng cổng mới.
`FRONTEND_API_URL` không điều khiển `scripts/dev.py`; script này ưu tiên backend local.

## 2. Schema và dữ liệu

Backend hiện tương thích bộ schema `sql/data/1.TaoCoSoDuLieu.sql`, seed
`sql/data/2.ThemDuLieu.sql`, rồi migration vai trò `sql/data/3.UpdateDeleteRangBuoc.sql`.
Hai file đầu có thao tác reset, chỉ dùng khi tạo database demo mới. Migration vai trò chạy
một lần nếu chưa có các cột `quyen_han`, `khu_vuc_quan_ly`.

Database local đang cấu hình đã có schema và dữ liệu, không cần khởi tạo lại.
Bộ `sql/schema/` + `sql/data/01_seed.sql` là bộ khác, không dùng lẫn với backend hiện tại.
Giá sản phẩm là `gia_san_pham`; chi tiết đơn không lưu đơn giá lúc bán. Doanh thu dashboard
được ước tính theo giá hiện tại. Analytics lượt truy cập là chức năng legacy, không cần
migration đó để chạy dashboard bán hàng.

## 3. Kiểm tra

```powershell
./scripts/test.ps1
py -3.13 scripts/check_queries.py
py -3.13 scripts/smoke_api.py
```

Frontend tests cần Node.js 22+. `scripts/test.ps1` thông báo nếu thiếu Node.
Để xác minh thêm đăng nhập và đọc dữ liệu theo vai trò:

```powershell
$env:SMOKE_PHONE = '0912000000'
$env:SMOKE_PASSWORD = 'NV000'
py -3.13 scripts/smoke_api.py --login
Remove-Item Env:SMOKE_PHONE, Env:SMOKE_PASSWORD
```

Kiểm tra API cổng khác:

```powershell
py -3.13 scripts/smoke_api.py --url http://127.0.0.1:8010 --origin http://127.0.0.1:8081
```

Smoke không ghi dữ liệu nghiệp vụ. Mặc định nó kiểm tra API công khai, HTTP 401 ở endpoint
được bảo vệ và CORS preflight. `--login` kiểm tra token, `/me`, dữ liệu phù hợp vai trò và
các trường hợp HTTP 403. Không in token/mật khẩu.

## 4. Backend trên Render

Dùng `render.yaml` hoặc cấu hình một Python Web Service với các giá trị từ project:

```text
Root Directory: để trống
Build Command: pip install -r backend/requirements.txt
Start Command: python -m uvicorn main:app --app-dir backend --host 0.0.0.0 --port $PORT
Health Check Path: /health
```

Gốc project phải còn `sql/app/` và `sql/query/`, nên không đặt Root Directory thành `backend`.
Cấp các biến `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `AUTH_TOKEN_SECRET`
trực tiếp cho tiến trình Render. GitHub Secrets không tự truyền sang Render.

`APP_CORS_ORIGINS` chứa origin frontend, ví dụ `https://ten-ban.github.io` hoặc domain riêng.
Origin chỉ gồm scheme + hostname + port, không có đường dẫn repository.
Backend hiện bổ sung các origin mặc định trong `backend/app/core/config.py`, bao gồm các cổng
local 8080, 5500, 5173 và các domain đã có trong project.

Có thể dùng `scripts/prepare_render_env.py` để tạo `.env.render` từ cấu hình local, kiểm tra
nội dung riêng rồi nhập vào môi trường backend. File này và `.env` được `.gitignore` loại trừ.
Nếu có CA, cấp secret file và đặt `DB_SSL_CA` tới đường dẫn file trên máy chủ.

Sau deploy, kiểm tra cả `/health`, `/api/health/db`, `/docs` và `POST /api/auth/login`.
API sống nhưng DB chưa cấu hình vẫn có thể trả 200 tại `/health`; chỉ endpoint DB mới xác
nhận đường kết nối database.

## 5. Frontend qua GitHub Pages

Workflow `.github/workflows/deploy.yml` chạy test, tạo `frontend/config.js` bằng
`scripts/build_frontend_config.py`, đóng gói `frontend/` rồi deploy Pages.

Cấu hình Actions Variable hoặc Secret `FRONTEND_API_URL` bằng URL HTTPS backend thật;
nếu cả hai tồn tại workflow ưu tiên Variable. Giá trị phải là URL FastAPI, không phải
hostname MySQL hay URL frontend. Bộ tạo config từ chối URL thiếu, HTTP, localhost,
private IP hoặc chứa thông tin đăng nhập.

```text
FRONTEND_API_URL=https://<backend-da-deploy>
APP_CORS_ORIGINS=https://<frontend-origin>
```

Trong repo dùng workflow này, chọn nguồn Pages là GitHub Actions rồi push nhánh `main`
hoặc chạy workflow thủ công. Artifact chỉ chứa frontend. Biến DB và khóa token ở backend.
File `frontend/config.js` đang có fallback public `https://fashion-manager.onrender.com`;
đây là giá trị trong source, chưa được xác minh là bản public hiện tại trong đợt làm việc này.

Sau deploy, có thể dùng:

```powershell
py -3.13 scripts/smoke_api.py --url https://<backend-da-deploy> --origin https://<frontend-origin>
```

`scripts/connect_backend.py` còn có khả năng đồng bộ cấu hình GitHub và kích hoạt workflow.
Chỉ chạy khi đã chọn đúng repository và chủ động muốn thay đổi cấu hình/deploy đó.

## 6. Workflow kiểm tra Aiven

`.github/workflows/verify-aiven.yml` dùng Secrets/Variables `DB_HOST`, `DB_PORT`, `DB_NAME`,
`DB_USER`, `DB_PASSWORD`. Có thể thêm `DB_SSL_CA_CERT` chứa nội dung CA.
Nó kiểm tra database chỉ đọc rồi dùng cùng hàm smoke như local. Các endpoint yêu cầu token
được kiểm tra phải trả 401 khi chưa đăng nhập, thay vì xem đó là lỗi kết nối.

## 7. Chẩn đoán lỗi

| Dấu hiệu | Kiểm tra |
| --- | --- |
| Không mở được frontend local | Terminal dev còn chạy, đúng cổng, không mở HTML bằng `file://` |
| API login HTTP 503 do khóa token | `AUTH_TOKEN_SECRET` có ít nhất 32 byte trên backend; khởi động lại sau khi sửa |
| Login HTTP 401 | Điện thoại tồn tại trong DB; mật khẩu đúng mã nhân viên |
| API HTTP 403 | Tài khoản có quyền chức năng và phạm vi cửa hàng/khu vực phù hợp |
| Login HTTP 404 | URL trỏ sai backend hoặc backend chưa có phiên bản API đăng nhập |
| Không gọi được API/CORS | URL FastAPI đúng, backend hoạt động, origin frontend được phép |
| DNS không phân giải | DB_HOST là hostname dịch vụ còn hoạt động, không phải tên hiển thị |
| Timeout hoặc connection refused | DB_PORT, dịch vụ MySQL, network/allowlist |
| Access denied | Tài khoản/mật khẩu DB và quyền trên database |
| Unknown database/table/column | DB_NAME và bộ schema hiện tại; không tự chạy lại seed/reset |
| Lỗi TLS | CA và hostname khớp cấu hình dịch vụ |
| Pages hiển thị nhưng số liệu không tải | Config.js đã trỏ đúng backend HTTPS, DB health, CORS, phiên đăng nhập |

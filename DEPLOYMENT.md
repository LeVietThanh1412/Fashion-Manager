# Chạy và triển khai schema v3

Khởi tạo database mới và quản trị đầu tiên theo [quy trình chính](README.md). Backend yêu cầu schema version 3. `reset-dev` chỉ dành cho database phát triển cục bộ đã xác minh, không dùng trên production.
Tài khoản dùng mật khẩu hash được cấp riêng, không có mật khẩu mặc định theo mã nhân viên.

```powershell
python -m pip install -r backend/requirements.txt
python scripts/verify_db.py
python scripts/dev.py --config dev.local.env
```

`verify_db.py` chỉ đọc database được cấu hình. Giữ riêng các biến DB và AUTH_TOKEN_SECRET ở backend.
Smoke chỉ đọc; tùy chọn `--login` dùng SMOKE_PHONE/SMOKE_PASSWORD do người vận hành cung cấp.

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
| Login HTTP 401 | Tài khoản active, nhân sự active, mật khẩu đã được đặt bằng quy trình cấp tài khoản |
| API HTTP 403 | Tài khoản có quyền chức năng và phạm vi cửa hàng/khu vực phù hợp |
| Login HTTP 404 | URL trỏ sai backend hoặc backend chưa có phiên bản API đăng nhập |
| Không gọi được API/CORS | URL FastAPI đúng, backend hoạt động, origin frontend được phép |
| DNS không phân giải | DB_HOST là hostname dịch vụ còn hoạt động, không phải tên hiển thị |
| Timeout hoặc connection refused | DB_PORT, dịch vụ MySQL, network/allowlist |
| Access denied | Tài khoản/mật khẩu DB và quyền trên database |
| Unknown database/table/column | DB_NAME và bộ schema hiện tại; không tự chạy lại seed/reset |
| Lỗi TLS | CA và hostname khớp cấu hình dịch vụ |
| Pages hiển thị nhưng số liệu không tải | Config.js đã trỏ đúng backend HTTPS, DB health, CORS, phiên đăng nhập |

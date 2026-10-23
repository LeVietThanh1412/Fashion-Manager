# Chạy và deploy Fashion Manager

Luồng dữ liệu: trình duyệt → frontend GitHub Pages → FastAPI chạy trên Render → Aiven MySQL.
GitHub Actions chạy test và đưa file tĩnh lên Pages; runner không phải máy chủ backend lâu dài.
GitHub Secrets chỉ cấp biến cho Actions, không tự cấp biến cho Render.

## Setup tự động cho repository này

Tài khoản chủ repo đã được xác nhận có GitHub Pro, nên GitHub Pages dùng được với repo private.
Giữ nguyên visibility theo lựa chọn của bạn. Public/private không gây lỗi DNS của MySQL.
Pages đã chuyển sang Source **GitHub Actions**; secrets DB đã được đồng bộ từ kết nối Aiven đang hoạt động.
Workflow Aiven đã chạy thành công sau khi đồng bộ.

Phần cần thực hiện một lần là tạo dịch vụ FastAPI trên Render. Có hai cách:

- **New → Blueprint**: kết nối repo và dùng `render.yaml`; Render tự đọc runtime, build/start command, gói Free và CORS.
- **New → Web Service** như màn hình hiện tại: điền các giá trị dưới đây và chọn instance **Free**.

```text
Language: Python 3
Branch: main
Root Directory: để trống
Build Command: pip install -r backend/requirements.txt
Start Command: python -m uvicorn main:app --app-dir backend --host 0.0.0.0 --port $PORT
Health Check Path: /health
Instance Type: Free
```

Đã tạo sẵn `.env.render` tại thư mục gốc, chứa thông tin Aiven đã kiểm tra và CORS cho domain Pages thực tế `https://thanhtech.cloud`.
Trong Render chọn **Add from .env** và dùng nội dung file này. File đã được `.gitignore` bảo vệ, không đưa lên GitHub.
Có thể tạo lại bằng `py -3.13 scripts/prepare_render_env.py`.

Sau khi Render báo Live và cấp URL HTTPS, tại máy chạy:

```powershell
# Dependency riêng cho script setup; không cần thêm vào backend production.
py -3.13 -m pip install PyNaCl
py -3.13 scripts/connect_backend.py https://URL-THAT-CUA-BAN.onrender.com
```

Script xác minh 7 endpoint thật và CORS, cập nhật secret `FRONTEND_API_URL`, đồng bộ Variable cùng tên nếu đang tồn tại, rồi tự chạy workflow deploy frontend.
Script dùng phiên GitHub của Git Credential Manager trên máy (hoặc `GH_TOKEN` trong môi trường); không in token hoặc mật khẩu.
Không thay URL ví dụ vào GitHub Secret: phải dùng URL dịch vụ Render đã triển khai thành công.

URL Pages của repo hiện được GitHub trả về là `https://thanhtech.cloud/Fashion-Manager/`.
Vì vậy origin backend cần cho phép `https://thanhtech.cloud`; Blueprint và file `.env.render` đã bao gồm cả domain này và origin GitHub mặc định.

## 1. Tự chạy với database Aiven thật

Dùng Python 3.12 hoặc 3.13. Trên máy hiện tại dùng `py -3.13`; `py -3` đang trỏ tới Python 3.8.
Chạy tại thư mục gốc repository:

```powershell
py -3.13 -m pip install -r backend/requirements.txt
# Chỉ tạo .env nếu chưa có; không ghi đè cấu hình đang dùng.
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Điền trong `.env`:

```dotenv
DB_HOST=your-service.aivencloud.com
DB_PORT=15000
DB_NAME=quan_ly_chuoi_thoi_trang
DB_USER=avnadmin
DB_PASSWORD=your_password
APP_CORS_ORIGINS=http://127.0.0.1:8080,http://localhost:8080
# Nếu đã tải CA certificate từ Aiven:
# DB_SSL_CA=C:/path/to/ca.pem
```

Host, port và user phải lấy từ **Aiven → service MySQL → Overview → Connection information**.
Port `15000` ở trên chỉ là ví dụ. `DB_NAME` phải là database đã chứa các bảng dự án.
Không tự chạy các file có `DROP DATABASE` lên Aiven đang có dữ liệu.

```powershell
py -3.13 scripts/verify_db.py
py -3.13 scripts/dev.py
```

Mở **http://127.0.0.1:8080**. API docs: **http://127.0.0.1:8000/docs**.
Ctrl+C dừng cả hai server và khôi phục `frontend/config.js` trước đó.
Nếu cổng 8000 đang dùng: `py -3.13 scripts/dev.py --api-port 8010`.
Script không tự seed dữ liệu. Các số tổng quan phản ánh cả dữ liệu seed đã nhập trước đó nếu DB đang chứa chúng.

### Dashboard quản lý cửa hàng

Trang chủ giữ bố cục biểu đồ, phân bố và bảng chi tiết nhưng dùng dữ liệu nghiệp vụ:

- 30 ngày gần nhất: số đơn hàng theo ngày và tổng giá trị `SUM(so_luong * don_gia_ban)`.
- Theo giờ: số đơn trong 30 ngày, đọc `ngay_tao_don` theo giờ địa phương Việt Nam.
- Sản phẩm theo danh mục: đếm sản phẩm thực tế, không thống kê điện thoại/máy tính.
- Đơn hàng gần nhất: tối đa 50 đơn trên toàn bộ thời gian, kèm mã khách, cửa hàng, số lượng và tổng giá trị.

API `/api/analytics/sales` chỉ đọc các bảng nghiệp vụ sẵn có. Không tạo lượt xem, không thu thập thiết bị/IP.
Khi chưa có đơn trong khoảng 30 ngày thì biểu đồ bằng 0; các đơn cũ vẫn có trong bảng gần nhất.
Khi DB lỗi, giao diện hiển thị lỗi thay vì thay bằng số 0 hoặc dữ liệu mẫu.

Mở terminal thứ hai để kiểm tra:

```powershell
py -3.13 -m pytest backend/tests -q
node --test frontend/tests/api.test.cjs
py -3.13 scripts/smoke_api.py
# Nếu chọn --api-port 8010:
py -3.13 scripts/smoke_api.py --url http://127.0.0.1:8010
```

Frontend tests cần Node.js 22+. Có thể chạy `./scripts/test.ps1` để chạy unit tests; script ghi rõ nếu thiếu Node.
Smoke test kiểm tra cả CORS cho origin frontend và đọc các endpoint thật; không ghi dữ liệu.

## 2. Backend trên Render

1. Đưa thay đổi code lên GitHub.
2. Tại Render, chọn **New → Blueprint**, kết nối repository và dùng `render.yaml`.
3. Điền `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` lấy từ Aiven.
4. `APP_CORS_ORIGINS=https://levietthanh1412.github.io` đã có trong Blueprint. CORS là origin, không thêm `/Fashion-Manager`. Nếu dùng domain khác, sửa lại biến này trên backend.
5. Có thể thêm **Secret File** tên `ca.pem`, dán CA certificate từ Aiven và thêm biến `DB_SSL_CA=/etc/secrets/ca.pem`. Khi có CA, backend xác minh cả chứng chỉ và hostname. Kết nối MySQL từ xa luôn phải được mã hóa TLS, kể cả chưa cấu hình CA.
6. Chờ service chạy rồi mở `https://<ten-service>.onrender.com/health` và `/api/health/db`. Cả hai phải trả `status: ok`.

Giữ **Root Directory trống** vì backend đọc SQL từ `sql/app` và `sql/query` ngoài thư mục `backend`.
Nếu tạo Web Service thủ công thay vì Blueprint:

```text
Build Command: pip install -r backend/requirements.txt
Start Command: python -m uvicorn main:app --app-dir backend --host 0.0.0.0 --port $PORT
Health Check Path: /health
```

## 3. Frontend qua GitHub Actions → GitHub Pages

1. Repository → **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. **Settings → Secrets and variables → Actions**: đặt `FRONTEND_API_URL` bằng URL HTTPS của backend Render, ví dụ `https://your-api.onrender.com`. Có thể để ở **Secrets** như cấu hình hiện tại hoặc **Variables**; workflow đọc cả hai, ưu tiên Variables nếu cùng tồn tại.
3. Push nhánh `main`, hoặc **Actions → CI and deploy frontend → Run workflow**.
4. Sau khi các job `test`, `build`, `deploy` thành công, mở `https://levietthanh1412.github.io/Fashion-Manager/`.

Không đặt `FRONTEND_API_URL` bằng hostname Aiven, URL GitHub Pages hoặc `localhost`. Biến này là URL **FastAPI** đang chạy.
Workflow tạo `frontend/config.js` bằng JSON hợp lệ và từ chối URL thiếu, HTTP hoặc localhost.
Artifact Pages chỉ chứa `frontend/`; không chứa `.env` hay mật khẩu DB.

## 4. Workflow kiểm tra Aiven và lỗi trong ảnh

`Verify Aiven database` chạy khi push `main` hoặc chạy thủ công trong Actions. Đây là kiểm tra tích hợp độc lập; lỗi Aiven vẫn báo đỏ và không giả lập kết quả thành công.
Các secrets hiện có `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` được giữ nguyên cách dùng.
`APP_CORS_ORIGINS` đọc được từ cả Secrets và Variables.
Có thể thêm secret `DB_SSL_CA_CERT` chứa **nội dung** CA certificate để CI xác minh danh tính máy chủ giống backend.

`Name or service not known` có nghĩa runner không phân giải được hostname. Việc secret đã tồn tại không xác nhận nội dung host đúng.
Backend xử lý khoảng trắng, dấu nháy bao ngoài, hostname kèm port và phần host của URI `mysql://...`.
Các trường user/password/database vẫn lấy riêng từ `DB_USER`, `DB_PASSWORD`, `DB_NAME`.
Nếu DNS tiếp tục lỗi, sửa giá trị secret `DB_HOST` bằng đúng **Host** trong Aiven Overview và kiểm tra service còn hoạt động.
GitHub không cho đọc lại giá trị secret qua API, nên cần đối chiếu tại nơi cấu hình.

| Dấu hiệu | Cần kiểm tra |
| --- | --- |
| DNS không phân giải | Host Aiven đúng, không phải tên hiển thị service; service còn tồn tại |
| Timeout / connection refused | Port Aiven, service đang chạy, network/IP allowlist |
| Access denied | User/password/quyền trên database |
| Unknown database / table | DB_NAME và schema thực tế; không tự reset database |
| Lỗi chứng chỉ TLS | CA đúng project Aiven và DB_HOST đúng hostname chứng chỉ |
| Pages tải được nhưng không có dữ liệu | Backend đang chạy; FRONTEND_API_URL là URL FastAPI; CORS cho phép origin Pages |

Kiểm tra sau deploy:

```powershell
py -3.13 scripts/smoke_api.py --url https://your-api.onrender.com --origin https://levietthanh1412.github.io
```

Tài liệu nền tảng: [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages), [Render FastAPI](https://render.com/docs/deploy-fastapi), [Aiven MySQL](https://aiven.io/docs/products/mysql/howto/connect-with-python).

## Vị trí nhập biến môi trường

Biến `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` phải có trên **Render → service Fashion-Manager → Environment → Add from .env**. Dùng nội dung `.env.render`, rồi **Save, rebuild, and deploy**. GitHub Secrets không tự được chuyển sang Render.

`frontend/config.js` hiện được commit với URL API công khai `https://fashion-manager.onrender.com`. Workflow vẫn tạo lại file từ `FRONTEND_API_URL`, kiểm tra cú pháp trước khi upload và kiểm tra HTTP sau deploy. `.env` và `.env.render` luôn được giữ ngoài Git.

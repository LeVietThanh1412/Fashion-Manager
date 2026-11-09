# Fashion Manager

Ứng dụng quản lý chuỗi cửa hàng thời trang trên MySQL 8.0.31+, FastAPI và giao diện tĩnh. Hai file SQL khởi tạo duy nhất nằm cùng trong [`sql/data`](sql/data): [`01_create_database.sql`](sql/data/01_create_database.sql) tạo database, bảng và view; [`02_seed_data.sql`](sql/data/02_seed_data.sql) đổ dữ liệu. `schema_version` lưu phiên bản và checksum để quản lý thay đổi sau này.

## Khởi tạo phát triển và đăng nhập

1. Tạo `dev.local.env` từ `.env.example`. Đặt `APP_ENV=development`, `DB_HOST=127.0.0.1`, `DB_PORT=3306` (hoặc cổng MySQL cục bộ), `DB_NAME=fashion_dev_local`, `DB_USER` và `AUTH_TOKEN_SECRET` riêng dài ít nhất 32 byte. Có thể để `DB_PASSWORD` trống: `scripts/dev.py` sẽ hỏi mật khẩu MySQL bằng nhập ẩn khi chạy. File này không được commit. Cài phụ thuộc: `pip install -r backend/requirements.txt`.
2. Tạo database mới và nạp demo, thay cổng và user cho đúng file cấu hình:

   ```powershell
   python scripts/database.py init --database fashion_dev_local --host 127.0.0.1 --port 3306 --user root --demo
   ```

   Script hỏi mật khẩu MySQL nếu chưa có `FASHION_LOCAL_DB_PASSWORD`. File dữ liệu có phần hệ thống (khu vực, chức vụ, vai trò và quyền) và phần demo tùy chọn qua `--demo` (cửa hàng, kho, nhân viên, tài khoản khóa, sản phẩm, khách hàng, đơn bán, phiếu điều chuyển và sổ biến động kho). Demo không chứa mật khẩu hoặc quyền quản trị.
3. Tạo quản trị đầu tiên bằng mật khẩu tự nhập:

   ```powershell
   python scripts/provision_account.py --database fashion_dev_local --port 3306 --user root --employee DEMO-ADMIN --account DEMO-ADMIN --bootstrap-admin
   ```

   Mật khẩu không hiển thị và không ghi vào SQL, source hoặc log. Script chỉ cấp `system_admin` khi chưa có phân công quản trị nào.
4. Chạy ứng dụng:

   ```powershell
   python scripts/dev.py --config dev.local.env
   ```

   Mở `http://127.0.0.1:8080`; đăng nhập bằng **0900000201** và mật khẩu vừa nhập. Số `+84900000201` hoặc `84900000201` cũng được chuẩn hóa về cùng tài khoản.

Để làm lại database phát triển đã xác minh, dùng lệnh sau. `reset-dev` chỉ chạy khi tên database, host, cổng và user trùng **chính xác** file `APP_ENV=development`, database có dạng `fashion_dev_*`, và host là loopback. Lệnh này xóa toàn bộ dữ liệu trong đúng database đó:

```powershell
python scripts/database.py reset-dev --database fashion_dev_local --host 127.0.0.1 --port 3306 --user root --config dev.local.env --demo
```

Sau reset cần chạy lại bước tạo quản trị. Không dùng lệnh reset trên production hoặc database từ xa. `status` chỉ đọc phiên bản; `init` chỉ cài trên database trống. Không có luồng nâng cấp dữ liệu phiên bản cũ.

## Tài khoản và quyền

Trang **Nhân sự** tạo hồ sơ, chức vụ và nơi làm việc; việc này không tự tạo tài khoản hay quyền. Người có quyền `employees.write` tạo tài khoản và cấp mật khẩu ban đầu chỉ cho nhân viên trong phạm vi quản lý của họ. Chỉ `auth.grant` cấp hệ thống mới được khóa/kích hoạt tài khoản, đặt lại mật khẩu hoặc gán/thu hồi vai trò. Nhân viên đăng nhập bằng số điện thoại và mật khẩu được cấp; trang **Tài khoản của tôi** cho phép đổi mật khẩu bằng cách xác minh mật khẩu hiện tại. Tài khoản chưa có phân công vẫn đăng nhập và xem trang cá nhân, nhưng API nghiệp vụ trả 403. Từng vai trò, phạm vi và quyền được hiển thị riêng.

Mật khẩu được hash bằng scrypt. Đổi/đặt lại mật khẩu hoặc khóa tài khoản tăng `auth_version`; khi tự đổi mật khẩu, phiên hiện tại được cấp token mới còn các phiên khác bị vô hiệu hóa. Mọi request nạp lại phân công đang hiệu lực; thu hồi quyền có hiệu lực ngay. Người cấp chỉ được giao một vai trò khi một phân công có `auth.grant` và `duoc_uy_quyen` của chính họ bao phủ toàn bộ quyền, phạm vi và thời hạn mới. API danh sách không trả mật khẩu hoặc hash.

Xem [ERD](reports/erd.md), [ma trận quyền](reports/permissions.md), [cấu trúc SQL](sql/README.md) và [hướng dẫn frontend](frontend/README.md).

## Kiểm thử

```powershell
python -m pytest backend/tests -q
$env:FASHION_TEST_MYSQL='1'; $env:FASHION_TEST_PORT='3308'; python -m pytest backend/tests/test_mysql.py -q
node --test frontend/tests/api.test.cjs
python scripts/check_queries.py
```

Kiểm thử MySQL chỉ dùng cổng riêng 3308 và tạo database `fashion_test_<UUID>` tạm thời. Bộ test mặc định bỏ qua phần MySQL khi không có biến opt in. `sql/tests/verify_seed.sql` đối chiếu số tồn với tổng biến động và kiểm tra tính toàn vẹn demo.

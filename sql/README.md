# SQL khởi tạo v3

Chỉ có **hai file khởi tạo/đổ dữ liệu**, cùng ở [`sql/data`](data):

| File | Nội dung |
| --- | --- |
| [`01_create_database.sql`](data/01_create_database.sql) | `CREATE DATABASE IF NOT EXISTS`, `CREATE TABLE IF NOT EXISTS` cho toàn bộ schema, `CREATE OR REPLACE VIEW`; database mặc định khi chạy trực tiếp là `fashion_dev_local` |
| [`02_seed_data.sql`](data/02_seed_data.sql) | Phần `-- @system` chứa khu vực, chức vụ, vai trò, quyền; phần `-- @demo` có 15 đơn hàng, 21 dòng hàng, 4 SKU, 2 cửa hàng và 2 phiếu điều chuyển, không chứa mật khẩu hoặc quyền quản trị đầu tiên |

Chạy theo [README](../README.md) bằng `scripts/database.py`. Runner thay tên database mặc định trong file tạo bằng `--database` đã kiểm tra, kiểm tra `schema_version` và trạng thái database trước khi chạy bảng/seed. `init` trên schema v3 đã cài sẽ không tạo hoặc nạp lại; database có bảng nhưng chưa có version sẽ bị từ chối. `reset-dev` chỉ xóa đúng database phát triển cục bộ đã khớp file cấu hình. `--demo` nạp phần demo trong **cùng file dữ liệu** sau khi cài mới.

Các file trong `sql/app` là truy vấn **được backend gọi khi chạy**, `sql/query` là bộ truy vấn học thuật, `sql/tests` là kiểm thử. Chúng không tạo database hay đổ dữ liệu và được giữ lại vì ứng dụng/kiểm thử còn dùng.

# Fashion Manager - BTL Cơ sở dữ liệu

**Chạy và deploy:** xem [DEPLOYMENT.md](DEPLOYMENT.md) để chạy frontend + API với Aiven thật tại máy, kiểm tra kết nối, và deploy frontend lên GitHub Pages bằng Actions, backend lên Render.

**Luồng kết nối và bản đồ chức năng:** xem [INTEGRATION.md](INTEGRATION.md) để biết từng màn hình gọi API nào, cách đăng nhập, phân quyền và kết quả kiểm tra tích hợp.

Đây là bài tập lớn quản lý chuỗi cửa hàng thời trang dùng MySQL, SQL tự viết trong `sql/app/`
và backend Python không ORM. Backend xác thực nhân viên bằng số điện thoại/mật khẩu, thực thi
phân quyền theo vai trò và giới hạn dữ liệu theo cửa hàng/khu vực. Xem
[DEPLOYMENT.md](DEPLOYMENT.md) để cấu hình khóa token và đăng nhập.

## Chạy kiểm tra không cần MySQL

```powershell
py -3 scripts\check_queries.py
```

## Schema database hiện hành

Ứng dụng khớp với schema được cung cấp trong `sql/data/` (giá sản phẩm là
`gia_san_pham`; chi tiết đơn hàng chỉ lưu mã sản phẩm và số lượng; vai trò là
tiếng Việt trong database). Trong một database demo, chạy lần lượt:

```text
sql/data/1.TaoCoSoDuLieu.sql
sql/data/2.ThemDuLieu.sql
sql/data/3.UpdateDeleteRangBuoc.sql
```

Hai file đầu có thao tác reset database, vì vậy chỉ dùng cho demo/test; migration thứ ba là
additive và không xóa dữ liệu. Không chạy lại chúng trên database thật đã có dữ liệu. Các file
trong `sql/schema/` và `sql/data/01_seed.sql` là bộ demo khác, không dùng chung với backend hiện
tại. Xem `.env.example` để cấu hình backend. Frontend static nằm trong
`frontend/` và gọi các endpoint backend để đọc dữ liệu MySQL; xem
[frontend/README.md](frontend/README.md) để chạy giao diện.

Schema hiện hành có `khu_vuc`: `1 = Miền Bắc`, `2 = Miền Trung`, `3 = Miền Nam`. Tài khoản đăng nhập bằng số điện thoại và mã nhân
viên làm mật khẩu. Admin trong database đang cấu hình đã được xác minh có số điện thoại `0912000000`, mật khẩu `NV000`. Bộ seed khác có thể dùng điện thoại `0901000000`; đăng nhập phải khớp dữ liệu DB thực tế. Đây là cơ chế đăng nhập demo.

Không commit `.env`, `AUTH_TOKEN_SECRET` hoặc thông tin đăng nhập MySQL. Render phải được cấu hình
riêng cho `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` và `AUTH_TOKEN_SECRET`.

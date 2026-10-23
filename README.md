# Fashion Manager - BTL Cơ sở dữ liệu

**Chạy và deploy:** xem [DEPLOYMENT.md](DEPLOYMENT.md) để chạy frontend + API với Aiven thật tại máy, kiểm tra kết nối, và deploy frontend lên GitHub Pages bằng Actions, backend lên Render.

Đây là bài tập lớn quản lý chuỗi cửa hàng thời trang dùng MySQL, SQL tự viết và backend
Python không ORM. Bắt đầu đọc [plans/README.md](plans/README.md), sau đó xem
[plans/PROGRESS.md](plans/PROGRESS.md).

## Chạy kiểm tra không cần MySQL

```powershell
py -3 scripts\check_queries.py
```

## Chạy MySQL demo

Trong một database demo cục bộ, chạy lần lượt:

```text
sql/schema/01_create_database.sql
sql/schema/02_create_tables.sql
sql/data/01_seed.sql
sql/tests/verify_seed.sql
```

`01_create_database.sql` có `DROP DATABASE` và chỉ được dùng cho demo/test. Không chạy trên
database thật. Xem `.env.example` để cấu hình backend. Frontend static nằm trong
`frontend/` và gọi các endpoint backend để đọc dữ liệu MySQL; xem
[frontend/README.md](frontend/README.md) để chạy giao diện.

Không commit `.env` hoặc thông tin đăng nhập MySQL. GitHub Actions đọc
`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` từ Repository Secrets.

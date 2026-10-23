# Fashion Manager - BTL Cơ sở dữ liệu

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
database thật. Xem `.env.example` để cấu hình backend. Frontend chưa được triển khai; đang
chờ template theo [frontend handoff](plans/08-frontend-handoff.md).
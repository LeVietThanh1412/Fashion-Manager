# Chương 3 - Cài đặt và khai thác

Database dùng MySQL 8.0.31+ với InnoDB/utf8mb4. Chạy schema theo thứ tự
`01_create_database.sql`, `02_create_tables.sql`, rồi `01_seed.sql`. Seed mục tiêu có 20
danh mục, 20 cửa hàng, 60 sản phẩm, 40 nhân viên, 40 phiếu phân phối, 120 dòng phân phối,
50 khách, 80 đơn và 160 dòng đơn.

Năm file `sql/query/member_01.sql` đến `member_05.sql` có đúng 50 mã query. `scripts/check_queries.py`
đã kiểm tra tĩnh và PASS 50 ID; việc chạy SQL thực tế cần MySQL server. Backend đọc statement
từ `sql/app`, bind parameter MySQL Connector/Python và không nhận raw SQL.

Kết quả integration và manual phải được cập nhật từ lệnh chạy thật; môi trường audit hiện
không có MySQL CLI/server nên không tuyên bố các phần đó PASS.

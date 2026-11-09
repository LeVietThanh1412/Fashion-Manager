> T?i li?u l?u tr? tr??c schema v3; kh?ng d?ng l?nh ho?c m? h?nh b?n d??i ?? kh?i t?o. Xem [quy tr?nh hi?n h?nh](../README.md), [ERD](erd.md) v? [ph?n quy?n](permissions.md).

# Kết quả kiểm tra tích hợp

Cập nhật theo workspace hiện tại ngày **27/10/2026**.

## Môi trường kiểm tra

- Workspace: `D:\abcdetuhoc\VTKH_prj\Fashion-Manager`.
- Windows; Python `3.14.6` từ `D:\Anaconda\python.exe`.
- Node.js và MySQL CLI không có trong `PATH`.
- Bộ schema/seed chính hiện nằm trong `sql/data/`; SQL ứng dụng nằm trong `sql/app/`.
- Bộ test MySQL là opt-in qua `FASHION_TEST_MYSQL=1` và yêu cầu MySQL thử nghiệm riêng tại `127.0.0.1:3308`. Không bật chế độ này và không ghi dữ liệu vào database.

## Kết quả đã chạy

| Kiểm tra | Kết quả |
| --- | --- |
| `python -m pytest backend/tests -q` | **81 passed, 1 failed, 31 skipped** |
| `python scripts/check_queries.py` | **PASS** — 5 file, 55 query ID duy nhất |
| `python -m compileall -q backend scripts` | **PASS** |
| `node --test frontend/tests/api.test.cjs` | **NOT RUN** — Node.js không có trong `PATH` |
| Kiểm tra tích hợp với MySQL thật | **NOT RUN** — bộ test MySQL cần opt-in và máy chủ thử nghiệm riêng |
| Kiểm tra thao tác trên trình duyệt | **NOT RUN** |

Một test hiện thất bại:

```text
backend/tests/test_application.py::test_no_redundant_current_price_or_detail_identifier_in_schema
FileNotFoundError: sql/1.TaoCoSoDuLieu.sql
```

Test đang tìm schema ở thư mục gốc `sql/`, trong khi file hiện có là
[`sql/data/1.TaoCoSoDuLieu.sql`](../sql/data/1.TaoCoSoDuLieu.sql). Đây là lỗi đường dẫn
trong test; test này chưa xác minh được các điều kiện schema. Không tự chuyển hoặc sửa file SQL
để làm test qua.

31 test bị skip thuộc nhóm MySQL tích hợp; chúng được cấu hình chỉ chạy khi đặt
`FASHION_TEST_MYSQL=1`. Không bật vì cần xác nhận rõ máy chủ MySQL riêng đúng `127.0.0.1:3308`;
test sẽ khởi tạo và ghi dữ liệu vào database test đó.

`compileall` chỉ xác nhận cú pháp Python, không thay thế kiểm tra chức năng frontend hoặc kết nối
database. Chưa có cơ sở để khẳng định API public, CORS, đăng nhập, dữ liệu MySQL, query explorer
trên backend đang chạy hay giao diện sau đăng nhập hoạt động trong lần kiểm tra này.

## Cần làm tiếp

1. Cập nhật test schema để đọc từ `sql/data/1.TaoCoSoDuLieu.sql`, hoặc dùng đường dẫn schema
   hiện hành phù hợp với mục tiêu kiểm tra; sau đó chạy lại toàn bộ backend tests.
2. Cài/chọn Node.js và chạy kiểm tra cú pháp JavaScript cùng
   `node --test frontend/tests/api.test.cjs`.
3. Chỉ chạy test MySQL tích hợp khi đã xác nhận database thử nghiệm riêng tại `127.0.0.1:3308`
   và cho phép test tạo/reset dữ liệu trong database đó.
4. Nếu cần báo cáo tích hợp end-to-end, khởi chạy frontend/backend và xác minh từng vai trò,
   CORS, thao tác đọc/ghi cùng giao diện trên môi trường được cho phép.

Không ghi nhận số lượng bản ghi, thông tin đăng nhập, trạng thái deploy hoặc kết quả kết nối
database trong báo cáo này vì chưa kiểm tra các mục đó trong workspace hiện tại.

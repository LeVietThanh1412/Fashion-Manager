# Kết quả kiểm tra kết nối ngày 26/10/2026

## Môi trường

- Workspace: `E:/LeVietThanh1412-Product/BTL_CSDL`.
- Python 3.13.5; Node từ runtime có sẵn trên máy (Node chưa có trong PATH thông thường).
- Frontend `http://127.0.0.1:8080`, backend `http://127.0.0.1:8000`.
- MySQL 8.4.11 qua cấu hình `.env` hiện có; kết nối từ xa được kiểm tra TLS.
- Không chạy seed/reset/migration hoặc thay đổi dữ liệu nghiệp vụ trên database.

## Kết quả

| Nhóm kiểm tra | Kết quả |
| --- | --- |
| `py -3.13 -m pytest backend/tests -q` | 58 passed; một cảnh báo deprecation từ thư viện Starlette/AnyIO |
| `node --test frontend/tests/api.test.cjs` | 10 passed |
| `node --check` cho api.js, app.js, charts.js | Passed |
| `py -3.13 -m compileall -q backend scripts` | Passed |
| `py -3.13 scripts/check_queries.py` | 5 file, 51 query ID duy nhất |
| DNS + `scripts/verify_db.py` | Passed; đọc được đủ 9 bảng nghiệp vụ |
| Public API và CORS | HTTP 200 cho health, DB health, sản phẩm, danh mục |
| Endpoint được bảo vệ khi chưa có token | HTTP 401 trên các endpoint được smoke test liệt kê |
| CORS preflight POST + authorization/content-type | Passed |
| Đăng nhập, `/me`, đọc dữ liệu với admin | Passed |
| Đăng nhập, `/me`, đọc dữ liệu với quản lý khu vực | Passed; query explorer và khách hàng trả 403 |
| Đăng nhập, `/me`, đọc dữ liệu với quản lý cửa hàng | Passed; query explorer và khách hàng trả 403 |
| Đăng nhập, `/me`, đọc dữ liệu với nhân viên | Passed; nhân viên và analytics sales trả 403 |
| Chạy toàn bộ query explorer bằng token admin trên API thật | 51/51 HTTP 200 |
| Config local cho cổng API tùy chọn | Test GET/HEAD/query string, no-store, không ghi đè file deploy đều qua |
| Frontend xử lý token hết hạn, lỗi validation, lỗi đồng bộ | Tests passed |
| Giao diện trong Edge | Trang đăng nhập local hiển thị; chưa xác minh thao tác sau đăng nhập qua UI |

Đăng nhập và đọc dữ liệu bốn vai trò được kiểm tra bằng HTTP tới backend đang chạy,
truy cập MySQL thật; không mock database ở đợt tích hợp này. Các luồng ghi như tạo đơn,
thêm nhân viên, cập nhật lương được kiểm tra trong bộ test với repository/connection giả lập;
không gửi thao tác ghi nghiệp vụ lên database thật.

Số dòng quan sát tại thời điểm kiểm tra:

| Bảng | Số dòng |
| --- | ---: |
| danh_muc | 20 |
| cua_hang | 20 |
| san_pham | 40 |
| nhan_vien | 74 |
| phan_phoi | 40 |
| chi_tiet_phan_phoi | 120 |
| khach_hang | 40 |
| don_hang | 100 |
| chi_tiet_don_hang | 230 |

Đối chiếu cuối xác nhận admin của database hiện tại là điện thoại `0912000000`, mật khẩu `NV000`. Đăng nhập qua HTTP, Bearer token và summary trả đúng 40 sản phẩm, 20 danh mục, 20 cửa hàng, 100 đơn hàng. Số `0901000000` trong tài liệu cũ thuộc bộ seed khác.

## Thay đổi

- Bổ sung khóa token ngẫu nhiên vào `.env` local, không đưa khóa vào source/frontend.
- Tách helper API khỏi các loader bị trùng trong `api.js` và `app.js`.
- Bỏ dữ liệu đăng nhập điền sẵn không khớp tài khoản seed.
- Ngăn submit đăng nhập lặp; xóa ô mật khẩu sau đăng nhập thành công.
- Tải dữ liệu ban đầu một lần cho mỗi endpoint, reset phân trang khi đăng nhập.
- Hiển thị chi tiết trường không hợp lệ khi backend trả HTTP 422.
- Sửa colspan thông báo bảng nhân viên từ 7 thành 5 cột.
- Dev server cấp config trong bộ nhớ, kiểm tra cổng/khóa token, chờ backend sẵn sàng và
  dừng frontend nếu backend kết thúc.
- Smoke test hỗ trợ đăng nhập bằng biến môi trường và kiểm tra quyền; workflow Aiven dùng
  chung hàm này, xử lý HTTP 401 đúng cho request chưa xác thực.
- Sửa fixture frontend để phản ánh các input/select thực tế trong HTML, thêm kiểm tra hồi quy.
- `requirements.txt` gốc tham chiếu dependencies backend.
- Bổ sung `INTEGRATION.md`, cập nhật README/frontend README/SQL README/DEPLOYMENT.md.

## Phạm vi bàn giao

Các thay đổi đang ở workspace local. Thư mục không có metadata Git, nên chưa commit/push.
Không thay đổi cấu hình Render/GitHub hoặc xác nhận bản public đã deploy cùng phiên bản.
Hướng dẫn chạy và map chức năng đầy đủ: [INTEGRATION.md](../INTEGRATION.md).

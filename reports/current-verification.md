# Kết quả kiểm chứng 2026-11-09

Đã hoàn thành schema v3 tạo mới, hai phần seed hệ thống/demo trong cùng một file, API và giao diện nhân sự/tài khoản/trang cá nhân, script tạo quản trị đầu tiên và reset phát triển có kiểm tra đích. Đã loại bỏ bảng rà soát/chuyển đổi dữ liệu cũ cùng nhánh nâng cấp tương ứng; `schema_version` và checksum vẫn được giữ.

Kiểm thử: `87 passed` trong `backend/tests` với MySQL 8.0.45 cục bộ cổng 3308; `16 passed` trong `frontend/tests/api.test.cjs`; `scripts/check_queries.py` xác nhận 77 truy vấn. Test MySQL bao gồm init mới, demo và đối chiếu tồn với ledger, reset đúng cấu hình, tạo quản trị đầu tiên, luồng nhân viên → tài khoản → mật khẩu → quyền → đăng nhập → phạm vi → thu hồi, tài khoản không quyền, đặt lại mật khẩu, khóa và kích hoạt. `git diff --check` không báo lỗi nội dung.

Chưa reset database mà `.env` hiện trỏ tới: host không phải loopback, không có `APP_ENV=development`, và tên database không thuộc `fashion_dev_*`. Cần một `dev.local.env` trỏ chính xác tới MySQL phát triển cục bộ cùng tên database, host, cổng, user; sau đó chạy lệnh `reset-dev` trong [README](../README.md). Không thực hiện thao tác phá hủy trên database từ xa.

# API và luồng dữ liệu hiện hành

Quy trình chạy duy nhất ở [README](README.md). Frontend gọi FastAPI bằng bearer token, backend truy cập MySQL theo schema v3. Không có tài khoản hoặc mật khẩu mặc định trong seed.

1. `POST /api/auth/login` nhận số di động Việt Nam và mật khẩu; số được chuẩn hóa về `+84…` duy nhất. `GET /api/auth/me` trả hồ sơ, chức vụ/nơi làm việc và từng phân công đang hiệu lực kèm quyền/phạm vi. `POST /api/auth/password` yêu cầu mật khẩu hiện tại và mật khẩu mới; API trả token mới cho phiên hiện tại.
2. `POST /api/employees` tạo hồ sơ với chức vụ và cửa hàng, không tạo tài khoản hay vai trò. `POST /api/access/accounts` tạo tài khoản riêng: người có `employees.write` chỉ tạo được cho nhân viên đang thuộc phạm vi của mình; mọi lượt cấp quyền được xác minh lại tại backend. `PUT /api/access/accounts/{id}/password` đặt lại mật khẩu và `PUT /api/access/accounts/{id}/status` kích hoạt/khóa; hai thao tác này yêu cầu `auth.grant` phạm vi hệ thống.
3. `POST /api/access/assignments` cấp vai trò nếu một phân công ủy quyền của người cấp bao phủ quyền, phạm vi và thời hạn đích. `POST /api/access/assignments/{id}/revoke` thu hồi. Quyền được nạp lại mỗi request; đổi/đặt lại mật khẩu hoặc khóa tài khoản vô hiệu hóa token cũ bằng `auth_version`.
4. Đơn bán lưu cửa hàng, kho và đơn giá/giảm giá lịch sử. Kho thay đổi qua giao dịch bán, hủy, điều chuyển hoặc kiểm kê; `ton_kho` và `bien_dong_kho` cập nhật trong cùng transaction.

Frontend chỉ hiện tab nghiệp vụ khi tài khoản có quyền tương ứng. API vẫn kiểm tra quyền cùng phạm vi. Tài khoản chưa được gán quyền chỉ xem được trang **Tài khoản của tôi**. Xem [ma trận quyền](reports/permissions.md) và [ERD](reports/erd.md).

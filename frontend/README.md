# Frontend

Chạy theo [quy trình khởi tạo và đăng nhập](../README.md): `python scripts/dev.py --config dev.local.env`, mở `http://127.0.0.1:8080`. `config.js` chỉ chứa URL API; bearer token giữ trong bộ nhớ trình duyệt.

Trang **Nhân sự** tạo hồ sơ, cập nhật nơi làm việc và trạng thái nhân sự trong phạm vi được cấp. Người có `employees.write` tạo tài khoản và mật khẩu ban đầu cho nhân viên thuộc phạm vi quản lý; chỉ quản trị hệ thống mới khóa/kích hoạt tài khoản, đặt lại mật khẩu hoặc gán/thu hồi vai trò. Nhân viên đổi mật khẩu tại **Tài khoản của tôi** bằng mật khẩu hiện tại; phiên mới tiếp tục hoạt động còn các phiên khác bị vô hiệu hóa. Trang cá nhân hiển thị từng vai trò với phạm vi và quyền tương ứng. Giao diện không đọc/hiển thị mật khẩu hash. Backend xác minh mọi quyền và phạm vi.

Form bán hàng dùng SKU, cửa hàng và kho trong phạm vi cho phép; lịch sử hỗ trợ xem chi tiết, hủy đơn và xuất CSV theo quyền. Báo cáo doanh thu cho phép chọn ngày và nhóm theo ngày/tháng/cửa hàng/nhân viên/khu vực. Trang kho hiển thị tồn và biến động, đồng thời cho phép kiểm kê, điều chuyển và hoàn tác phiếu trong đúng phạm vi. Tài khoản chưa có quyền không thấy tab nghiệp vụ và API nghiệp vụ trả 403.

```powershell
node --check frontend/js/app.js
node --test frontend/tests/api.test.cjs
```

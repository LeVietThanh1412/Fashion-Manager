# Frontend

Xem [DEPLOYMENT.md](../DEPLOYMENT.md) để chạy tại máy và deploy GitHub Pages + backend + Aiven.

Frontend là HTML/CSS/JavaScript tĩnh. `index.html` gọi `js/api.js` và `js/app.js`.
`fashion_manager_admin_dashboard.html` chuyển hướng về `index.html`.
`config.js` chứa URL backend công khai, được tạo khi deploy. `scripts/dev.py` phục vụ config local trong bộ nhớ với đúng cổng API, không ghi đè file này.

Xem [INTEGRATION.md](../INTEGRATION.md) để đối chiếu từng màn hình với API và luồng xác thực.

Người dùng đăng nhập bằng số điện thoại và mã nhân viên làm mật khẩu. Token chỉ giữ trong bộ nhớ
của trang; tải lại trang sẽ yêu cầu đăng nhập lại. Sidebar thay đổi theo vai trò, nhưng quyền truy
cập luôn được kiểm tra ở API/backend.

Sản phẩm, danh mục, cửa hàng và số tổng quan đều lấy từ API/MySQL.
Không có mảng dữ liệu mẫu hoặc biểu đồ giả. Phân trang sản phẩm dùng `limit`/`offset` của API.
Trang chủ thống kê doanh thu theo quyền admin/khu vực/cửa hàng. Nhân viên có tab tạo đơn và xem
số lượng phân phối thuộc cửa hàng mình. Dữ liệu phân phối không phải tồn kho hiện tại.
`js/charts.js` lấy dữ liệu từ `/api/analytics/sales`, đọc các bảng nghiệp vụ hiện có.
Không thu thập thiết bị/IP khi mở trang. Bốn số tổng quan nghiệp vụ nằm trong Thông tin chung.
Khi tải lỗi, trang hiển thị lỗi, xóa số tổng quan cũ và không thông báo đồng bộ thành công.
Admin có tab **Truy vấn dữ liệu** để chọn và chạy các truy vấn đã được backend đăng ký từ
`sql/query/`; kết quả hiển thị theo cột trả về và giới hạn tối đa 500 dòng. Giao diện không cho nhập
hoặc sửa SQL tùy ý.
Giá đơn hàng và doanh thu lịch sử được ước tính bằng giá hiện tại của sản phẩm vì schema không lưu
đơn giá tại thời điểm bán. Schema hiện tại cũng không có cột trạng thái nhân viên, nên giao diện
không hiển thị thao tác vô hiệu hóa/kích hoạt tài khoản. Tải trang chỉ đọc dữ liệu; tạo đơn và các
thao tác quản trị chỉ ghi dữ liệu khi người dùng chủ động gửi biểu mẫu.

Chạy từ thư mục gốc bằng Python 3.12/3.13:

```powershell
py -3.13 -m pip install -r backend/requirements.txt
py -3.13 scripts/dev.py
```

Mở `http://127.0.0.1:8080`. Backend dùng `.env` tại thư mục gốc; dữ liệu không được tự tạo hoặc reset.
Nếu cổng API đang bận, dùng `py -3.13 scripts/dev.py --api-port 8010`.

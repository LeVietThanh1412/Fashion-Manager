# Frontend

Xem [DEPLOYMENT.md](../DEPLOYMENT.md) để chạy tại máy và deploy GitHub Pages + backend + Aiven.

Frontend là HTML/CSS/JavaScript tĩnh. `index.html` gọi `js/api.js` và `js/app.js`.
`fashion_manager_admin_dashboard.html` chuyển hướng về `index.html`.
`config.js` chứa URL backend công khai, được tạo khi deploy hoặc chạy `scripts/dev.py`.

Sản phẩm, danh mục, số sản phẩm mỗi danh mục, cửa hàng và bốn số tổng quan đều lấy từ API/MySQL.
Không có mảng dữ liệu mẫu hoặc biểu đồ giả. Phân trang sản phẩm dùng `limit`/`offset` của API.
Trang chủ hiển thị lượt truy cập thật từ `luot_truy_cap_web`; chạy `py -3.13 scripts/init_analytics.py` một lần để tạo bảng.
`js/charts.js` vẽ biểu đồ và bảng lượt xem từ API; bốn số tổng quan nghiệp vụ nằm trong Thông tin chung.
Khi tải lỗi, trang hiển thị lỗi, xóa số tổng quan cũ và không thông báo đồng bộ thành công.

Chạy từ thư mục gốc bằng Python 3.12/3.13:

```powershell
py -3.13 -m pip install -r backend/requirements.txt
py -3.13 scripts/dev.py
```

Mở `http://127.0.0.1:8080`. Backend dùng `.env` tại thư mục gốc; dữ liệu không được tự tạo hoặc reset.
Nếu cổng API đang bận, dùng `py -3.13 scripts/dev.py --api-port 8010`.

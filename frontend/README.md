# Frontend

Frontend là static HTML, gọi trực tiếp backend API để đọc dữ liệu MySQL:

```powershell
cd E:\LeVietThanh1412-Product\Fashion-Manager\frontend
py -3 -m http.server 8080
```

Mở `http://localhost:8080` (hoặc cổng static server bạn chọn).

- `index.html`: markup và nội dung giao diện Admin/POS.
- `styles.css`: toàn bộ CSS, không còn style inline trong HTML.
- `js/api.js`: gọi API backend và hiển thị trạng thái loading/error/empty.
- `js/app.js`, `js/charts.js`: tương tác menu và các thành phần dashboard.

Backend chạy riêng:

```powershell
cd E:\LeVietThanh1412-Product\Fashion-Manager
$env:PYTHONPATH = "backend"
py -3.13 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend không có dữ liệu mẫu. Hãy cấu hình `.env` ở thư mục gốc trước khi chạy
backend; trạng thái kết nối sẽ hiển thị trong thẻ “Database đang kết nối” trên sidebar.

Trình duyệt không tự đọc được `.env`. URL backend công khai của frontend nằm trong
`config.js` và không chứa thông tin database:

```powershell
Copy-Item config.js.example config.js
```

Trong CI/deploy, tạo file này từ biến public `FRONTEND_API_URL` (GitHub Actions
Variable), tuyệt đối không đưa `DB_PASSWORD` vào frontend.
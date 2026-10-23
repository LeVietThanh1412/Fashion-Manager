# Frontend demo

Frontend hiện là static HTML để chạy nhanh, không cần bundler:

```powershell
cd E:\LeVietThanh1412-Product\Fashion-Manager\frontend
py -3 -m http.server 8080
```

Mở `http://localhost:8080`.

- `index.html`: markup và nội dung giao diện Admin/POS.
- `styles.css`: toàn bộ CSS, không còn style inline trong HTML.
- `app.js`: tương tác menu, lọc danh mục, giỏ hàng, tính tổng tiền và checkout demo.

Backend chạy riêng:

```powershell
cd E:\LeVietThanh1412-Product\Fashion-Manager
$env:PYTHONPATH = "backend"
py -3.13 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
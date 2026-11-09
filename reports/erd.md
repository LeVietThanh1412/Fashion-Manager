# ERD hiện hành (schema v3)

[`sql/data/01_create_database.sql`](../sql/data/01_create_database.sql) là định nghĩa chuẩn. Sơ đồ tách hồ sơ, chức vụ/nơi làm việc, tài khoản và phân quyền:

```mermaid
erDiagram
  khu_vuc ||--o{ cua_hang : contains
  khu_vuc ||--o{ kho : central_region
  cua_hang ||--o{ kho : store_stock
  nhan_vien ||--o{ phan_cong_lam_viec : works
  chuc_vu ||--o{ phan_cong_lam_viec : position
  cua_hang ||--o{ phan_cong_lam_viec : workplace
  kho ||--o{ phan_cong_lam_viec : workplace
  nhan_vien ||--o| tai_khoan : login
  tai_khoan ||--o{ phan_cong_quyen : assigned
  vai_tro ||--o{ phan_cong_quyen : role
  vai_tro ||--o{ vai_tro_quyen : includes
  quyen ||--o{ vai_tro_quyen : permission
  danh_muc ||--o{ mau_san_pham : groups
  mau_san_pham ||--o{ san_pham : variants
  kho ||--o{ ton_kho : holds
  san_pham ||--o{ ton_kho : quantity
  ton_kho ||--o{ bien_dong_kho : ledger
  khach_hang ||--o{ don_hang : buys
  nhan_vien ||--o{ don_hang : sells
  cua_hang ||--o{ don_hang : store
  kho ||--o{ don_hang : stock_source
  don_hang ||--|{ chi_tiet_don_hang : items
  san_pham ||--o{ chi_tiet_don_hang : sku
  nhan_vien ||--o{ phan_phoi : handles
  kho ||--o{ phan_phoi : source_or_target
  phan_phoi ||--|{ chi_tiet_phan_phoi : items
  san_pham ||--o{ chi_tiet_phan_phoi : sku
  tai_khoan ||--o{ bien_dong_kho : actor
  don_hang ||--o{ bien_dong_kho : sale_effect
  phan_phoi ||--o{ bien_dong_kho : transfer_effect
```

`phan_cong_lam_viec` giữ thời hạn, chức vụ và **một** nơi làm việc (cửa hàng hoặc kho) mỗi dòng. `phan_cong_quyen` giữ vai trò, thời hạn, trạng thái, khả năng ủy quyền và **một** phạm vi (hệ thống, khu vực, cửa hàng hoặc kho) mỗi dòng. Hai loại phân công độc lập. `ma_quan_ly` chỉ mô tả quan hệ báo cáo nhân sự; nó không cấp quyền.

Mỗi nhân viên có tối đa một tài khoản, số điện thoại nhân viên được lưu dạng `+84…` duy nhất. `auth_version` vô hiệu hóa token khi khóa hoặc đổi mật khẩu. `schema_version` lưu phiên bản/checksum cho các thay đổi sau này.

Giá bán và tổng giảm giá trên `chi_tiet_don_hang` là ảnh chụp tại lúc bán và luôn có giá trị. `don_hang` luôn chỉ rõ cửa hàng/kho, `phan_phoi` luôn chỉ rõ kho nguồn/đích. `ton_kho.so_luong` phải bằng tổng `bien_dong_kho.so_luong` theo từng kho/SKU; backend cập nhật cả hai trong cùng transaction. Seed demo tính số tồn trực tiếp từ ledger.

INSERT INTO nhan_vien (
    ma_nhan_vien, ho_ten, so_dien_thoai, email, ma_cua_hang,
    ma_quan_ly, quyen_han, khu_vuc_quan_ly, luong, trang_thai
)
VALUES (
    %(employee_id)s, %(name)s, %(phone)s, %(email)s, %(store_id)s,
    %(manager_id)s, %(role)s, %(region_id)s, %(salary)s, 'active'
);

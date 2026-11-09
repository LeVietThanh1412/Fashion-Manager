SELECT nv.ma_nhan_vien,nv.ho_ten,nv.so_dien_thoai,nv.email,nv.ma_quan_ly,nv.luong,tk.ma_tai_khoan,tk.mat_khau_hash,tk.auth_version,
CASE WHEN nv.trang_thai='active' THEN tk.trang_thai ELSE 'inactive' END AS trang_thai
FROM tai_khoan tk JOIN nhan_vien nv ON nv.ma_nhan_vien=tk.ma_nhan_vien
WHERE tk.ma_tai_khoan=%(account_id)s;

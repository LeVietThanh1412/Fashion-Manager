SELECT nv.ma_nhan_vien, nv.ho_ten, nv.so_dien_thoai, nv.email,
       nv.quyen_han, nv.khu_vuc_quan_ly, nv.ma_cua_hang,
       nv.luong, nv.trang_thai, ch.ten_cua_hang,
       ch.khu_vuc AS store_region
FROM nhan_vien AS nv
LEFT JOIN cua_hang AS ch ON ch.ma_cua_hang = nv.ma_cua_hang
WHERE (
    %(actor_role)s = 'admin'
    OR (%(actor_role)s = 'regional_manager' AND ch.khu_vuc = %(actor_region)s)
    OR (%(actor_role)s = 'store_manager'
        AND nv.ma_cua_hang = %(actor_store)s
        AND nv.quyen_han = 'staff')
)
ORDER BY nv.ho_ten, nv.ma_nhan_vien;

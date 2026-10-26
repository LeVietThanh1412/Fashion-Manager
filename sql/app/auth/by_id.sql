SELECT nv.ma_nhan_vien, nv.ho_ten, nv.so_dien_thoai, nv.quyen_han,
       nv.khu_vuc_quan_ly, nv.ma_cua_hang, nv.trang_thai,
       ch.khu_vuc AS store_region
FROM nhan_vien AS nv
LEFT JOIN cua_hang AS ch ON ch.ma_cua_hang = nv.ma_cua_hang
WHERE nv.ma_nhan_vien = %(employee_id)s
LIMIT 1;

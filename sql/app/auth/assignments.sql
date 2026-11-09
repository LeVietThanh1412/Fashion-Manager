SELECT pc.*,vq.ma_quyen FROM phan_cong_quyen pc
JOIN vai_tro_quyen vq ON vq.ma_vai_tro=pc.ma_vai_tro
WHERE pc.ma_tai_khoan=%(account_id)s AND pc.thu_hoi_luc IS NULL
AND pc.trang_thai='active'
AND pc.tu_ngay<=UTC_TIMESTAMP(6) AND (pc.den_ngay IS NULL OR UTC_TIMESTAMP(6)<pc.den_ngay)
ORDER BY pc.ma_phan_cong,vq.ma_quyen;

SELECT ma_san_pham, ma_danh_muc, ten_san_pham, mau_sac, kich_co, gia_ban
FROM san_pham
WHERE ma_san_pham = %(product_id)s;

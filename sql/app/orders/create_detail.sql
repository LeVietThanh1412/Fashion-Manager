INSERT INTO chi_tiet_don_hang
    (ma_chi_tiet, ma_don_hang, ma_san_pham, so_luong, don_gia_ban)
VALUES (%(detail_id)s, %(order_id)s, %(product_id)s, %(quantity)s, %(unit_price)s);

SELECT sp.ma_san_pham, sp.ten_san_pham, sp.mau_sac, sp.kich_co,
       COALESCE(SUM(ctpp.so_luong), 0) AS so_luong_phan_phoi
FROM san_pham AS sp
JOIN chi_tiet_phan_phoi AS ctpp ON ctpp.ma_san_pham = sp.ma_san_pham
JOIN phan_phoi AS pp ON pp.ma_phan_phoi = ctpp.ma_phan_phoi
WHERE pp.ma_cua_hang = %(store_id)s
GROUP BY sp.ma_san_pham, sp.ten_san_pham, sp.mau_sac, sp.kich_co
ORDER BY sp.ten_san_pham, sp.ma_san_pham;

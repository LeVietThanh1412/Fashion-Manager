SELECT dm.ma_danh_muc, dm.ten_danh_muc, COUNT(sp.ma_san_pham) AS so_san_pham
FROM danh_muc AS dm
LEFT JOIN san_pham AS sp ON sp.ma_danh_muc = dm.ma_danh_muc
GROUP BY dm.ma_danh_muc, dm.ten_danh_muc
ORDER BY dm.ten_danh_muc, dm.ma_danh_muc;

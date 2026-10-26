SELECT dm.ma_danh_muc AS id, dm.ten_danh_muc AS name,
       COUNT(sp.ma_san_pham) AS count
FROM danh_muc AS dm
LEFT JOIN san_pham AS sp ON sp.ma_danh_muc = dm.ma_danh_muc
GROUP BY dm.ma_danh_muc, dm.ten_danh_muc
ORDER BY count DESC, dm.ma_danh_muc;

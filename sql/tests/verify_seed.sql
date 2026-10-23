USE quan_ly_chuoi_thoi_trang;
SELECT 'danh_muc' AS table_name, COUNT(*) AS row_count FROM danh_muc
UNION ALL SELECT 'cua_hang', COUNT(*) FROM cua_hang
UNION ALL SELECT 'san_pham', COUNT(*) FROM san_pham
UNION ALL SELECT 'nhan_vien', COUNT(*) FROM nhan_vien
UNION ALL SELECT 'phan_phoi', COUNT(*) FROM phan_phoi
UNION ALL SELECT 'chi_tiet_phan_phoi', COUNT(*) FROM chi_tiet_phan_phoi
UNION ALL SELECT 'khach_hang', COUNT(*) FROM khach_hang
UNION ALL SELECT 'don_hang', COUNT(*) FROM don_hang
UNION ALL SELECT 'chi_tiet_don_hang', COUNT(*) FROM chi_tiet_don_hang;

SELECT COUNT(*) AS orphan_products FROM san_pham p
LEFT JOIN danh_muc d ON d.ma_danh_muc = p.ma_danh_muc
WHERE d.ma_danh_muc IS NULL;
SELECT COUNT(*) AS orphan_order_details FROM chi_tiet_don_hang ct
LEFT JOIN don_hang d ON d.ma_don_hang = ct.ma_don_hang
WHERE d.ma_don_hang IS NULL;

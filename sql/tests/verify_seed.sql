-- Read-only checks after a fresh v3 init with --demo. Every error query should return zero rows.
SELECT version,checksum,source FROM schema_version;
SELECT ma_vai_tro,COUNT(*) AS permission_count FROM vai_tro_quyen GROUP BY ma_vai_tro;
SELECT s.ma_san_pham FROM san_pham s LEFT JOIN mau_san_pham m ON m.ma_mau=s.ma_mau WHERE m.ma_mau IS NULL;
SELECT ct.ma_don_hang FROM chi_tiet_don_hang ct LEFT JOIN don_hang d ON d.ma_don_hang=ct.ma_don_hang WHERE d.ma_don_hang IS NULL;
SELECT t.ma_kho,t.ma_san_pham,t.so_luong,COALESCE(SUM(b.so_luong),0) AS ledger_quantity
FROM ton_kho t LEFT JOIN bien_dong_kho b ON b.ma_kho=t.ma_kho AND b.ma_san_pham=t.ma_san_pham
GROUP BY t.ma_kho,t.ma_san_pham,t.so_luong HAVING t.so_luong<>COALESCE(SUM(b.so_luong),0);
SELECT d.ma_don_hang FROM don_hang d LEFT JOIN kho k ON k.ma_kho=d.ma_kho
WHERE k.ma_cua_hang<>d.ma_cua_hang OR k.ma_kho IS NULL;
SELECT p.ma_phan_phoi FROM phan_phoi p LEFT JOIN kho k ON k.ma_kho=p.ma_kho_dich
WHERE k.ma_cua_hang<>p.ma_cua_hang OR k.ma_kho IS NULL;
SELECT ct.ma_don_hang,ct.ma_san_pham FROM chi_tiet_don_hang ct
WHERE ct.don_gia_ban IS NULL OR ct.giam_gia IS NULL;

-- Minh hoa UPDATE, DELETE va cac rang buoc. Du lieu nghiep vu duoc ROLLBACK.
USE quan_ly_chuoi_thoi_trang;

START TRANSACTION;
INSERT INTO khach_hang (ma_khach_hang,ho_ten,so_dien_thoai)
VALUES ('KH_DEMO_DML','Khach hang kiem thu','0999999998');
UPDATE khach_hang SET ho_ten='Khach hang da cap nhat' WHERE ma_khach_hang='KH_DEMO_DML';
SELECT * FROM khach_hang WHERE ma_khach_hang='KH_DEMO_DML';
DELETE FROM khach_hang WHERE ma_khach_hang='KH_DEMO_DML';
ROLLBACK;

-- Procedure bat loi de co the chay lien tuc cac vi du khong hop le.
DELIMITER $$
DROP PROCEDURE IF EXISTS minh_hoa_rang_buoc$$
CREATE PROCEDURE minh_hoa_rang_buoc()
BEGIN
    DECLARE bi_chan BOOLEAN DEFAULT FALSE;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET bi_chan=TRUE;
    START TRANSACTION;

    SET bi_chan=FALSE;
    INSERT INTO danh_muc SELECT * FROM danh_muc WHERE ma_danh_muc='DM001';
    SELECT 'Khoa chinh trung' AS tinh_huong, bi_chan AS da_bi_chan;

    SET bi_chan=FALSE;
    INSERT INTO san_pham VALUES ('SP_DEMO_FK','KHONG_TON_TAI','San pham loi FK','Den','40',1000);
    SELECT 'Khoa ngoai khong ton tai' AS tinh_huong, bi_chan AS da_bi_chan;

    SET bi_chan=FALSE;
    UPDATE san_pham SET gia_san_pham=-1 WHERE ma_san_pham='SP001';
    SELECT 'CHECK gia am' AS tinh_huong, bi_chan AS da_bi_chan;

    SET bi_chan=FALSE;
    UPDATE chi_tiet_don_hang SET so_luong=0 WHERE ma_don_hang='DH001';
    SELECT 'CHECK so luong bang 0' AS tinh_huong, bi_chan AS da_bi_chan;

    SET bi_chan=FALSE;
    UPDATE nhan_vien SET luong=-1 WHERE ma_nhan_vien='NV024';
    SELECT 'CHECK luong am' AS tinh_huong, bi_chan AS da_bi_chan;

    SET bi_chan=FALSE;
    UPDATE cua_hang SET khu_vuc=4 WHERE ma_cua_hang='CH001';
    SELECT 'CHECK khu vuc khong hop le' AS tinh_huong, bi_chan AS da_bi_chan;

    SET bi_chan=FALSE;
    UPDATE nhan_vien SET khu_vuc_quan_ly=1 WHERE ma_nhan_vien='NV024';
    SELECT 'CHECK vai tro va pham vi' AS tinh_huong, bi_chan AS da_bi_chan;

    SET bi_chan=FALSE;
    DELETE FROM danh_muc WHERE ma_danh_muc='DM001';
    SELECT 'Khong xoa danh muc dang co san pham' AS tinh_huong, bi_chan AS da_bi_chan;
    ROLLBACK;
END$$
CALL minh_hoa_rang_buoc()$$
DROP PROCEDURE minh_hoa_rang_buoc$$
DELIMITER ;

-- Moi bang nghiep vu/lich su deu co it nhat 20 dong trong file 2.
SELECT 'danh_muc' AS bang, COUNT(*) AS so_dong FROM danh_muc
UNION ALL SELECT 'san_pham',COUNT(*) FROM san_pham
UNION ALL SELECT 'cua_hang',COUNT(*) FROM cua_hang
UNION ALL SELECT 'nhan_vien',COUNT(*) FROM nhan_vien
UNION ALL SELECT 'phan_phoi',COUNT(*) FROM phan_phoi
UNION ALL SELECT 'chi_tiet_phan_phoi',COUNT(*) FROM chi_tiet_phan_phoi
UNION ALL SELECT 'khach_hang',COUNT(*) FROM khach_hang
UNION ALL SELECT 'don_hang',COUNT(*) FROM don_hang
UNION ALL SELECT 'chi_tiet_don_hang',COUNT(*) FROM chi_tiet_don_hang
UNION ALL SELECT 'lich_su_quan_ly',COUNT(*) FROM lich_su_quan_ly;

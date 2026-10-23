USE quan_ly_chuoi_thoi_trang;

-- Run in a test transaction only; rollback keeps the deterministic seed unchanged.
START TRANSACTION;
INSERT INTO khach_hang (ma_khach_hang, ho_ten, so_dien_thoai)
VALUES ('KH_TEST_DML', 'Khach hang DML', '0900000099');
UPDATE khach_hang SET ho_ten = 'Khach hang DML updated'
WHERE ma_khach_hang = 'KH_TEST_DML';
DELETE FROM khach_hang WHERE ma_khach_hang = 'KH_TEST_DML';
ROLLBACK;

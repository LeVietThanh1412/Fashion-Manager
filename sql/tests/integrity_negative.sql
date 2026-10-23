USE quan_ly_chuoi_thoi_trang;

-- Execute each statement separately in a disposable test database.
-- Every statement must be rejected by a real PK/FK/UNIQUE/CHECK/NOT NULL constraint.
INSERT INTO danh_muc (ma_danh_muc, ten_danh_muc) VALUES ('DM01', 'Trung khoa');
INSERT INTO san_pham (ma_san_pham, ma_danh_muc, ten_san_pham, mau_sac, kich_co, gia_ban)
VALUES ('NEG_FK', 'DM_DOES_NOT_EXIST', 'Invalid', 'Den', 'M', 100);
INSERT INTO san_pham (ma_san_pham, ma_danh_muc, ten_san_pham, mau_sac, kich_co, gia_ban)
VALUES ('NEG_CHECK', 'DM01', 'Invalid price', 'Den', 'M', -1);
INSERT INTO khach_hang (ma_khach_hang, ho_ten, so_dien_thoai)
VALUES ('NEG_NULL', NULL, '0900000000');

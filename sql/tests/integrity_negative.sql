-- Run each statement separately after the demo section of sql/data/02_seed_data.sql in an isolated v3 test DB.
-- All must fail with a real PK/FK/UNIQUE/CHECK constraint. These are NOT deployment seeds.
INSERT INTO khu_vuc VALUES (1,'Duplicate region');
INSERT INTO san_pham (ma_san_pham,ma_mau,mau_sac,kich_co,gia_san_pham)
VALUES ('NEG_FK','MISSING','Black','39',100);
INSERT INTO san_pham (ma_san_pham,ma_mau,mau_sac,kich_co,gia_san_pham)
VALUES ('NEG_PRICE','DEMO-M1','Black','41',-1);
INSERT INTO san_pham (ma_san_pham,ma_mau,mau_sac,kich_co,gia_san_pham)
VALUES ('NEG_DUP','DEMO-M1','Black','39',100);
INSERT INTO ton_kho VALUES ('DEMO-K1','DEMO-SKU1',-1);
INSERT INTO khach_hang VALUES ('NEG_NULL',NULL,'0999999999');
INSERT INTO nhan_vien (ma_nhan_vien,ho_ten,so_dien_thoai,email,luong)
VALUES ('NEG_PHONE','Invalid phone','0900000201','invalid@example.test',1000);
INSERT INTO don_hang (ma_don_hang,ma_nhan_vien,ma_khach_hang,ma_cua_hang,ma_kho)
VALUES ('NEG_ORDER','DEMO-SELLER','DEMO-C1','DEMO-S1',NULL);
INSERT INTO chi_tiet_don_hang (ma_don_hang,ma_san_pham,so_luong,don_gia_ban,giam_gia)
VALUES ('DEMO-O1','DEMO-SKU3',1,NULL,0);

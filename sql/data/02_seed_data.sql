-- @system
-- Deployment catalog only. No people, accounts, passwords, orders or stock.
INSERT IGNORE INTO khu_vuc VALUES (1,'Mien Bac'),(2,'Mien Trung'),(3,'Mien Nam');
INSERT INTO chuc_vu VALUES ('director','Director'),('manager','Manager'),('sales','Sales Associate'),('warehouse','Warehouse Associate');
INSERT INTO vai_tro VALUES ('system_admin','System Admin');
INSERT INTO vai_tro VALUES ('operations_manager','Operations Manager');
INSERT INTO vai_tro VALUES ('regional_manager','Regional Manager');
INSERT INTO vai_tro VALUES ('store_manager','Store Manager');
INSERT INTO vai_tro VALUES ('sales_staff','Sales Staff');
INSERT INTO vai_tro VALUES ('warehouse_staff','Warehouse Staff');
INSERT INTO quyen VALUES ('catalog.read','Read product and category catalog');
INSERT INTO quyen VALUES ('stores.read','Read stores in scope');
INSERT INTO quyen VALUES ('employees.read','Read personnel in scope');
INSERT INTO quyen VALUES ('employees.write','Edit personnel and work placements in scope');
INSERT INTO quyen VALUES ('employees.salary','Edit salary in scope');
INSERT INTO quyen VALUES ('sales.read','Read orders in scope');
INSERT INTO quyen VALUES ('sales.create','Sell SKU stock in scope');
INSERT INTO quyen VALUES ('sales.cancel','Cancel orders in scope');
INSERT INTO quyen VALUES ('reports.read','Read and export sales reports in scope');
INSERT INTO quyen VALUES ('inventory.read','Read stock and movements in scope');
INSERT INTO quyen VALUES ('inventory.adjust','Record counted stock adjustments in scope');
INSERT INTO quyen VALUES ('inventory.transfer','Transfer stock between authorized warehouses');
INSERT INTO quyen VALUES ('customers.read','Read customers associated with scoped orders');
INSERT INTO quyen VALUES ('customers.write','Register customers for sales');
INSERT INTO quyen VALUES ('auth.grant','Delegate roles within a delegable assignment');
INSERT INTO quyen VALUES ('queries.execute','Run registered global academic queries');
INSERT INTO quyen VALUES ('analytics.read','Read global web analytics');
INSERT INTO vai_tro_quyen VALUES ('system_admin','analytics.read');
INSERT INTO vai_tro_quyen VALUES ('system_admin','auth.grant');
INSERT INTO vai_tro_quyen VALUES ('system_admin','catalog.read');
INSERT INTO vai_tro_quyen VALUES ('system_admin','customers.read');
INSERT INTO vai_tro_quyen VALUES ('system_admin','customers.write');
INSERT INTO vai_tro_quyen VALUES ('system_admin','employees.read');
INSERT INTO vai_tro_quyen VALUES ('system_admin','employees.salary');
INSERT INTO vai_tro_quyen VALUES ('system_admin','employees.write');
INSERT INTO vai_tro_quyen VALUES ('system_admin','inventory.adjust');
INSERT INTO vai_tro_quyen VALUES ('system_admin','inventory.read');
INSERT INTO vai_tro_quyen VALUES ('system_admin','inventory.transfer');
INSERT INTO vai_tro_quyen VALUES ('system_admin','queries.execute');
INSERT INTO vai_tro_quyen VALUES ('system_admin','reports.read');
INSERT INTO vai_tro_quyen VALUES ('system_admin','sales.cancel');
INSERT INTO vai_tro_quyen VALUES ('system_admin','sales.create');
INSERT INTO vai_tro_quyen VALUES ('system_admin','sales.read');
INSERT INTO vai_tro_quyen VALUES ('system_admin','stores.read');
INSERT INTO vai_tro_quyen VALUES ('operations_manager','catalog.read');
INSERT INTO vai_tro_quyen VALUES ('operations_manager','customers.read');
INSERT INTO vai_tro_quyen VALUES ('operations_manager','customers.write');
INSERT INTO vai_tro_quyen VALUES ('operations_manager','employees.read');
INSERT INTO vai_tro_quyen VALUES ('operations_manager','employees.salary');
INSERT INTO vai_tro_quyen VALUES ('operations_manager','employees.write');
INSERT INTO vai_tro_quyen VALUES ('operations_manager','inventory.adjust');
INSERT INTO vai_tro_quyen VALUES ('operations_manager','inventory.read');
INSERT INTO vai_tro_quyen VALUES ('operations_manager','inventory.transfer');
INSERT INTO vai_tro_quyen VALUES ('operations_manager','reports.read');
INSERT INTO vai_tro_quyen VALUES ('operations_manager','sales.cancel');
INSERT INTO vai_tro_quyen VALUES ('operations_manager','sales.create');
INSERT INTO vai_tro_quyen VALUES ('operations_manager','sales.read');
INSERT INTO vai_tro_quyen VALUES ('operations_manager','stores.read');
INSERT INTO vai_tro_quyen VALUES ('regional_manager','catalog.read');
INSERT INTO vai_tro_quyen VALUES ('regional_manager','employees.read');
INSERT INTO vai_tro_quyen VALUES ('regional_manager','employees.salary');
INSERT INTO vai_tro_quyen VALUES ('regional_manager','employees.write');
INSERT INTO vai_tro_quyen VALUES ('regional_manager','inventory.read');
INSERT INTO vai_tro_quyen VALUES ('regional_manager','inventory.transfer');
INSERT INTO vai_tro_quyen VALUES ('regional_manager','reports.read');
INSERT INTO vai_tro_quyen VALUES ('regional_manager','sales.cancel');
INSERT INTO vai_tro_quyen VALUES ('regional_manager','sales.read');
INSERT INTO vai_tro_quyen VALUES ('regional_manager','stores.read');
INSERT INTO vai_tro_quyen VALUES ('store_manager','catalog.read');
INSERT INTO vai_tro_quyen VALUES ('store_manager','customers.read');
INSERT INTO vai_tro_quyen VALUES ('store_manager','customers.write');
INSERT INTO vai_tro_quyen VALUES ('store_manager','employees.read');
INSERT INTO vai_tro_quyen VALUES ('store_manager','employees.salary');
INSERT INTO vai_tro_quyen VALUES ('store_manager','employees.write');
INSERT INTO vai_tro_quyen VALUES ('store_manager','inventory.read');
INSERT INTO vai_tro_quyen VALUES ('store_manager','reports.read');
INSERT INTO vai_tro_quyen VALUES ('store_manager','sales.cancel');
INSERT INTO vai_tro_quyen VALUES ('store_manager','sales.create');
INSERT INTO vai_tro_quyen VALUES ('store_manager','sales.read');
INSERT INTO vai_tro_quyen VALUES ('store_manager','stores.read');
INSERT INTO vai_tro_quyen VALUES ('sales_staff','catalog.read');
INSERT INTO vai_tro_quyen VALUES ('sales_staff','customers.read');
INSERT INTO vai_tro_quyen VALUES ('sales_staff','customers.write');
INSERT INTO vai_tro_quyen VALUES ('sales_staff','inventory.read');
INSERT INTO vai_tro_quyen VALUES ('sales_staff','sales.create');
INSERT INTO vai_tro_quyen VALUES ('sales_staff','sales.read');
INSERT INTO vai_tro_quyen VALUES ('sales_staff','stores.read');
INSERT INTO vai_tro_quyen VALUES ('warehouse_staff','catalog.read');
INSERT INTO vai_tro_quyen VALUES ('warehouse_staff','inventory.adjust');
INSERT INTO vai_tro_quyen VALUES ('warehouse_staff','inventory.read');
INSERT INTO vai_tro_quyen VALUES ('warehouse_staff','inventory.transfer');
-- @demo
-- Fictional demo on a fresh v3 schema. Passwords and administrator grants are never seeded.
INSERT INTO danh_muc VALUES ('SHOE','Shoes'),('SHIRT','Shirts');
INSERT INTO cua_hang (ma_cua_hang,ten_cua_hang,khu_vuc,dia_chi,so_dien_thoai,email) VALUES
('DEMO-S1','Hanoi flagship',1,'1 Demo Street, Hanoi','0900000101','s1@example.test'),
('DEMO-S2','Danang branch',2,'2 Demo Street, Danang','0900000102','s2@example.test');
INSERT INTO kho (ma_kho,ten_kho,loai_kho,ma_cua_hang,ma_khu_vuc) VALUES
('DEMO-CENTRAL','North distribution center','central',NULL,1),
('DEMO-K1','Hanoi stock','store','DEMO-S1',NULL),
('DEMO-K2','Danang stock','store','DEMO-S2',NULL);
INSERT INTO nhan_vien (ma_nhan_vien,ho_ten,so_dien_thoai,email,luong) VALUES
('DEMO-ADMIN','Demo Administrator','+84900000201','admin@example.test',20000000),
('DEMO-SELLER','Demo Sales Associate','+84900000202','seller@example.test',10000000),
('DEMO-SELLER2','Demo Danang Associate','+84900000203','seller2@example.test',10000000),
('DEMO-WAREHOUSE','Demo Warehouse Associate','+84900000204','warehouse@example.test',11000000);
INSERT INTO phan_cong_lam_viec (ma_nhan_vien,ma_chuc_vu,ma_cua_hang,ma_kho) VALUES
('DEMO-ADMIN','director','DEMO-S1',NULL),('DEMO-SELLER','sales','DEMO-S1',NULL),
('DEMO-SELLER2','sales','DEMO-S2',NULL),('DEMO-WAREHOUSE','warehouse',NULL,'DEMO-CENTRAL');
INSERT INTO tai_khoan (ma_tai_khoan,ma_nhan_vien) VALUES
('DEMO-ADMIN','DEMO-ADMIN'),('DEMO-SELLER','DEMO-SELLER'),
('DEMO-SELLER2','DEMO-SELLER2'),('DEMO-WAREHOUSE','DEMO-WAREHOUSE');
INSERT INTO phan_cong_quyen (ma_tai_khoan,ma_vai_tro,pham_vi,ma_cua_hang) VALUES
('DEMO-SELLER','sales_staff','store','DEMO-S1'),('DEMO-SELLER2','sales_staff','store','DEMO-S2');
INSERT INTO phan_cong_quyen (ma_tai_khoan,ma_vai_tro,pham_vi,ma_kho) VALUES
('DEMO-WAREHOUSE','warehouse_staff','warehouse','DEMO-CENTRAL');
INSERT INTO mau_san_pham (ma_mau,ma_danh_muc,ten_san_pham) VALUES
('DEMO-M1','SHOE','Everyday sneaker'),('DEMO-M2','SHIRT','Oxford shirt');
INSERT INTO san_pham (ma_san_pham,ma_mau,mau_sac,kich_co,gia_san_pham) VALUES
('DEMO-SKU1','DEMO-M1','Black','39',699000),
('DEMO-SKU2','DEMO-M1','White','40',599000),('DEMO-SKU3','DEMO-M2','Blue','M',449000);
INSERT INTO khach_hang VALUES ('DEMO-C1','Demo Customer One','0900000301'),
('DEMO-C2','Demo Customer Two','0900000302');
INSERT INTO don_hang (ma_don_hang,ma_nhan_vien,ma_khach_hang,ma_cua_hang,ma_kho,ngay_tao_don) VALUES
('DEMO-O1','DEMO-SELLER','DEMO-C1','DEMO-S1','DEMO-K1','2026-11-01 10:00:00'),
('DEMO-O2','DEMO-SELLER2','DEMO-C2','DEMO-S2','DEMO-K2','2026-11-02 15:00:00');
-- Saved sale price is historical; SKU1 currently costs 699000.
INSERT INTO chi_tiet_don_hang VALUES
('DEMO-O1','DEMO-SKU1',2,599000,98000),('DEMO-O1','DEMO-SKU2',1,649000,0),
('DEMO-O2','DEMO-SKU1',3,599000,0);
INSERT INTO phan_phoi (ma_phan_phoi,ma_nhan_vien,ma_cua_hang,ma_kho_nguon,ma_kho_dich,ngay_phan_phoi) VALUES
('DEMO-T1','DEMO-WAREHOUSE','DEMO-S1','DEMO-CENTRAL','DEMO-K1','2026-10-30'),
('DEMO-T2','DEMO-WAREHOUSE','DEMO-S2','DEMO-CENTRAL','DEMO-K2','2026-10-31');
INSERT INTO chi_tiet_phan_phoi VALUES
('DEMO-T1','DEMO-SKU1',20),('DEMO-T1','DEMO-SKU2',10),('DEMO-T2','DEMO-SKU1',15);
-- Stock keys start at zero for FK integrity; final balances derive only from the ledger.
INSERT INTO ton_kho (ma_kho,ma_san_pham,so_luong) VALUES
('DEMO-CENTRAL','DEMO-SKU1',0),('DEMO-CENTRAL','DEMO-SKU2',0),
('DEMO-K1','DEMO-SKU1',0),('DEMO-K1','DEMO-SKU2',0),('DEMO-K2','DEMO-SKU1',0);
INSERT INTO bien_dong_kho (ma_kho,ma_san_pham,so_luong,loai,ly_do,ma_tai_khoan,ma_don_hang,ma_phan_phoi,tao_luc) VALUES
('DEMO-CENTRAL','DEMO-SKU1',100,'adjustment','Counted receipt','DEMO-WAREHOUSE',NULL,NULL,'2026-10-29 08:00:00'),
('DEMO-CENTRAL','DEMO-SKU2',60,'adjustment','Counted receipt','DEMO-WAREHOUSE',NULL,NULL,'2026-10-29 08:00:00'),
('DEMO-CENTRAL','DEMO-SKU1',-20,'transfer','Dispatch T1','DEMO-WAREHOUSE',NULL,'DEMO-T1','2026-10-30 09:00:00'),
('DEMO-K1','DEMO-SKU1',20,'transfer','Receive T1','DEMO-WAREHOUSE',NULL,'DEMO-T1','2026-10-30 09:00:00'),
('DEMO-CENTRAL','DEMO-SKU2',-10,'transfer','Dispatch T1','DEMO-WAREHOUSE',NULL,'DEMO-T1','2026-10-30 09:00:00'),
('DEMO-K1','DEMO-SKU2',10,'transfer','Receive T1','DEMO-WAREHOUSE',NULL,'DEMO-T1','2026-10-30 09:00:00'),
('DEMO-CENTRAL','DEMO-SKU1',-15,'transfer','Dispatch T2','DEMO-WAREHOUSE',NULL,'DEMO-T2','2026-10-31 09:00:00'),
('DEMO-K2','DEMO-SKU1',15,'transfer','Receive T2','DEMO-WAREHOUSE',NULL,'DEMO-T2','2026-10-31 09:00:00'),
('DEMO-K1','DEMO-SKU1',-2,'sale','Sale O1','DEMO-SELLER','DEMO-O1',NULL,'2026-11-01 10:00:00'),
('DEMO-K1','DEMO-SKU2',-1,'sale','Sale O1','DEMO-SELLER','DEMO-O1',NULL,'2026-11-01 10:00:00'),
('DEMO-K2','DEMO-SKU1',-3,'sale','Sale O2','DEMO-SELLER2','DEMO-O2',NULL,'2026-11-02 15:00:00');
UPDATE ton_kho tk JOIN (SELECT ma_kho,ma_san_pham,SUM(so_luong) AS balance FROM bien_dong_kho
GROUP BY ma_kho,ma_san_pham) ledger ON ledger.ma_kho=tk.ma_kho AND ledger.ma_san_pham=tk.ma_san_pham
SET tk.so_luong=ledger.balance;

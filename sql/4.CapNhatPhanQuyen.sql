-- Cap nhat CSDL CU. Khong DROP DATABASE, khong nap lai du lieu mau.
-- Chay sau khi da chon dung database. Co the chay lai.
-- Khong can chay file nay neu da tao moi bang file 1 va 2.
USE quan_ly_chuoi_thoi_trang;

DELIMITER $$
DROP PROCEDURE IF EXISTS cap_nhat_phan_quyen$$
CREATE PROCEDURE cap_nhat_phan_quyen()
BEGIN
    DECLARE them_quyen BOOLEAN DEFAULT FALSE;
    DECLARE ten_khoa_ngoai VARCHAR(64) DEFAULT NULL;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='nhan_vien' AND column_name='quyen_han') THEN
        ALTER TABLE nhan_vien ADD COLUMN quyen_han ENUM('admin','regional_manager','store_manager','staff') NOT NULL DEFAULT 'staff';
        SET them_quyen = TRUE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='nhan_vien' AND column_name='khu_vuc_quan_ly') THEN
        ALTER TABLE nhan_vien ADD COLUMN khu_vuc_quan_ly TINYINT NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='nhan_vien' AND column_name='luong') THEN
        ALTER TABLE nhan_vien ADD COLUMN luong DECIMAL(12,2) NOT NULL DEFAULT 0;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='nhan_vien' AND column_name='cap_bac') THEN
        ALTER TABLE nhan_vien ADD COLUMN cap_bac TINYINT NOT NULL DEFAULT 2 COMMENT '1: Thu viec, 2: Chinh thuc, 3: Truong ca';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='nhan_vien' AND column_name='trang_thai') THEN
        ALTER TABLE nhan_vien ADD COLUMN trang_thai ENUM('active','inactive') NOT NULL DEFAULT 'active';
    END IF;

    -- Chi suy ra quyen khi vua them cot, khong ghi de phan cong da chinh sua.
    IF them_quyen THEN
        UPDATE nhan_vien SET quyen_han='admin' WHERE ma_cua_hang IS NULL AND ma_quan_ly IS NULL;
        UPDATE nhan_vien nv
        JOIN (SELECT DISTINCT ma_quan_ly FROM nhan_vien WHERE ma_quan_ly IS NOT NULL) ql ON ql.ma_quan_ly=nv.ma_nhan_vien
        SET nv.quyen_han=CASE WHEN nv.ma_cua_hang IS NULL THEN 'regional_manager' ELSE 'store_manager' END
        WHERE nv.quyen_han <> 'admin';
        UPDATE nhan_vien nv JOIN (
            SELECT n.ma_quan_ly,MIN(ch.khu_vuc) AS khu_vuc,COUNT(DISTINCT ch.khu_vuc) AS so_khu_vuc
            FROM nhan_vien n JOIN cua_hang ch ON ch.ma_cua_hang=n.ma_cua_hang GROUP BY n.ma_quan_ly
        ) v ON v.ma_quan_ly=nv.ma_nhan_vien
        SET nv.khu_vuc_quan_ly=v.khu_vuc
        WHERE nv.quyen_han='regional_manager' AND v.so_khu_vuc=1;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.statistics WHERE table_schema=DATABASE() AND table_name='nhan_vien' AND index_name='uq_mot_chu_thuong_hieu') THEN
        CREATE UNIQUE INDEX uq_mot_chu_thuong_hieu ON nhan_vien
            ((CASE WHEN quyen_han='admin' AND trang_thai='active' THEN 1 ELSE NULL END));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.statistics WHERE table_schema=DATABASE() AND table_name='nhan_vien' AND index_name='uq_quan_ly_khu_vuc') THEN
        CREATE UNIQUE INDEX uq_quan_ly_khu_vuc ON nhan_vien
            ((CASE WHEN quyen_han='regional_manager' AND trang_thai='active' THEN khu_vuc_quan_ly ELSE NULL END));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.statistics WHERE table_schema=DATABASE() AND table_name='nhan_vien' AND index_name='uq_quan_ly_cua_hang') THEN
        CREATE UNIQUE INDEX uq_quan_ly_cua_hang ON nhan_vien
            ((CASE WHEN quyen_han='store_manager' AND trang_thai='active' THEN ma_cua_hang ELSE NULL END));
    END IF;

    -- BCNF: nguoi nhan da xac dinh cua hang, khong luu lap lai tren phieu.
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='phan_phoi' AND column_name='ma_cua_hang') THEN
        IF EXISTS (SELECT 1 FROM phan_phoi pp JOIN nhan_vien nv ON nv.ma_nhan_vien=pp.ma_nhan_vien WHERE nv.ma_cua_hang IS NULL OR pp.ma_cua_hang<>nv.ma_cua_hang) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Nhan vien nhan khac cua hang: sua phan cong truoc khi chuan hoa phan_phoi.';
        END IF;
        SELECT constraint_name INTO ten_khoa_ngoai
        FROM information_schema.key_column_usage
        WHERE table_schema=DATABASE() AND table_name='phan_phoi' AND column_name='ma_cua_hang' AND referenced_table_name IS NOT NULL LIMIT 1;
        IF ten_khoa_ngoai IS NOT NULL THEN
            SET @lenh_bo_fk=CONCAT('ALTER TABLE phan_phoi DROP FOREIGN KEY `',REPLACE(ten_khoa_ngoai,'`','``'),'`');
            PREPARE lenh FROM @lenh_bo_fk;
            EXECUTE lenh;
            DEALLOCATE PREPARE lenh;
        END IF;
        ALTER TABLE phan_phoi DROP COLUMN ma_cua_hang;
    END IF;

    -- Chi gia_san_pham la gia hien hanh. Don gia tren don la gia lich su rieng.
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='san_pham' AND column_name='gia_san_pham') THEN
        ALTER TABLE san_pham RENAME COLUMN gia_ban TO gia_san_pham;
    ELSEIF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='san_pham' AND column_name='gia_ban') THEN
        IF EXISTS (SELECT 1 FROM san_pham WHERE gia_ban <> gia_san_pham) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Hai cot gia khac nhau: doi chieu du lieu truoc khi bo gia_ban.';
        END IF;
        ALTER TABLE san_pham DROP COLUMN gia_ban;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='chi_tiet_don_hang' AND column_name='don_gia_ban') THEN
        ALTER TABLE chi_tiet_don_hang ADD COLUMN don_gia_ban DECIMAL(15,0) NULL;
        -- Du lieu cu khong co gia lich su: khoi tao mot lan bang gia hien tai.
        -- Khong the khoi phuc chinh xac gia cu neu truoc day chua luu.
        UPDATE chi_tiet_don_hang ct JOIN san_pham sp ON sp.ma_san_pham=ct.ma_san_pham SET ct.don_gia_ban=sp.gia_san_pham;
        ALTER TABLE chi_tiet_don_hang MODIFY COLUMN don_gia_ban DECIMAL(15,0) NOT NULL;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='chi_tiet_don_hang' AND column_name='ma_chi_tiet') THEN
        -- Khoa ghep (ma_don_hang,ma_san_pham) da du xac dinh mot dong.
        ALTER TABLE chi_tiet_don_hang DROP COLUMN ma_chi_tiet;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_schema=DATABASE() AND table_name='chi_tiet_don_hang' AND constraint_type='CHECK' AND constraint_name='ck_don_gia_ban') THEN
        ALTER TABLE chi_tiet_don_hang ADD CONSTRAINT ck_don_gia_ban CHECK (don_gia_ban >= 0);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_schema=DATABASE() AND table_name='nhan_vien' AND constraint_name='ck_cap_bac') THEN
        ALTER TABLE nhan_vien ADD CONSTRAINT ck_cap_bac CHECK (cap_bac BETWEEN 1 AND 3);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_schema=DATABASE() AND table_name='nhan_vien' AND constraint_name='ck_luong') THEN
        ALTER TABLE nhan_vien ADD CONSTRAINT ck_luong CHECK (luong IS NULL OR luong >= 0);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_schema=DATABASE() AND table_name='nhan_vien' AND constraint_name='ck_pham_vi') THEN
        ALTER TABLE nhan_vien ADD CONSTRAINT ck_pham_vi CHECK (
            (quyen_han='admin' AND ma_cua_hang IS NULL AND khu_vuc_quan_ly IS NULL)
            OR (quyen_han='regional_manager' AND ma_cua_hang IS NULL AND khu_vuc_quan_ly IS NOT NULL AND khu_vuc_quan_ly IN (1,2,3))
            OR (quyen_han IN ('store_manager','staff') AND ma_cua_hang IS NOT NULL AND khu_vuc_quan_ly IS NULL)
        );
    END IF;
END$$
CALL cap_nhat_phan_quyen()$$
DROP PROCEDURE cap_nhat_phan_quyen$$
DELIMITER ;

CREATE TABLE IF NOT EXISTS lich_su_quan_ly (
    ma_lich_su INT AUTO_INCREMENT PRIMARY KEY,
    ma_nhan_vien VARCHAR(20) NOT NULL,
    quyen_han ENUM('regional_manager','store_manager') NOT NULL,
    ma_cua_hang VARCHAR(20),
    khu_vuc_quan_ly TINYINT,
    tu_ngay DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    den_ngay DATETIME,
    FOREIGN KEY (ma_nhan_vien) REFERENCES nhan_vien(ma_nhan_vien),
    FOREIGN KEY (ma_cua_hang) REFERENCES cua_hang(ma_cua_hang),
    CONSTRAINT ck_lich_su_ngay CHECK (den_ngay IS NULL OR den_ngay >= tu_ngay),
    CONSTRAINT ck_lich_su_pham_vi CHECK (
        (quyen_han='regional_manager' AND ma_cua_hang IS NULL AND khu_vuc_quan_ly IS NOT NULL AND khu_vuc_quan_ly IN (1,2,3))
        OR (quyen_han='store_manager' AND ma_cua_hang IS NOT NULL AND khu_vuc_quan_ly IS NULL)
    )
) ENGINE=InnoDB;

INSERT INTO lich_su_quan_ly (ma_nhan_vien,quyen_han,ma_cua_hang,khu_vuc_quan_ly)
SELECT nv.ma_nhan_vien,nv.quyen_han,nv.ma_cua_hang,nv.khu_vuc_quan_ly
FROM nhan_vien nv
WHERE nv.quyen_han IN ('regional_manager','store_manager') AND nv.trang_thai='active'
AND NOT EXISTS (SELECT 1 FROM lich_su_quan_ly ls WHERE ls.ma_nhan_vien=nv.ma_nhan_vien AND ls.den_ngay IS NULL);

SELECT ma_nhan_vien,ho_ten,quyen_han,ma_cua_hang,khu_vuc_quan_ly,luong,cap_bac,trang_thai
FROM nhan_vien ORDER BY ma_nhan_vien;

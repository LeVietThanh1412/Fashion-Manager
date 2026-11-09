-- @database
-- Default local target. scripts/database.py substitutes the validated --database name.
CREATE DATABASE IF NOT EXISTS `fashion_dev_local` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `fashion_dev_local`;
-- @tables
-- Canonical fresh baseline v3. MySQL 8.0.31+; select the target database before running.
-- No seed data, destructive reset, triggers or application business rules here.
CREATE TABLE IF NOT EXISTS schema_version (
    version INT PRIMARY KEY,
    checksum CHAR(64) NOT NULL,
    installed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS khu_vuc (
    ma_khu_vuc INT PRIMARY KEY,
    ten_khu_vuc VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS cua_hang (
    ma_cua_hang VARCHAR(20) PRIMARY KEY,
    ten_cua_hang VARCHAR(255) NOT NULL,
    khu_vuc INT NOT NULL,
    dia_chi VARCHAR(255) NOT NULL,
    so_dien_thoai VARCHAR(25) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    trang_thai VARCHAR(10) NOT NULL DEFAULT 'active',
    CONSTRAINT ck_ch_status CHECK (trang_thai IN ('active','inactive')),
    CONSTRAINT fk_ch_region FOREIGN KEY (khu_vuc) REFERENCES khu_vuc(ma_khu_vuc)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS kho (
    ma_kho VARCHAR(20) PRIMARY KEY,
    ten_kho VARCHAR(255) NOT NULL,
    loai_kho VARCHAR(10) NOT NULL,
    ma_cua_hang VARCHAR(20) NULL,
    ma_khu_vuc INT NULL,
    trang_thai VARCHAR(10) NOT NULL DEFAULT 'active',
    UNIQUE KEY uq_kho_store (ma_kho,ma_cua_hang),
    CONSTRAINT fk_kho_store FOREIGN KEY (ma_cua_hang) REFERENCES cua_hang(ma_cua_hang),
    CONSTRAINT fk_kho_region FOREIGN KEY (ma_khu_vuc) REFERENCES khu_vuc(ma_khu_vuc),
    CONSTRAINT ck_kho_type CHECK (
        (loai_kho='store' AND ma_cua_hang IS NOT NULL AND ma_khu_vuc IS NULL)
        OR (loai_kho='central' AND ma_cua_hang IS NULL)),
    CONSTRAINT ck_kho_status CHECK (trang_thai IN ('active','inactive'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS nhan_vien (
    ma_nhan_vien VARCHAR(20) PRIMARY KEY,
    ho_ten VARCHAR(255) NOT NULL,
    so_dien_thoai VARCHAR(12) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    ma_quan_ly VARCHAR(20) NULL,
    luong DECIMAL(15,2) NOT NULL,
    trang_thai VARCHAR(10) NOT NULL DEFAULT 'active',
    CONSTRAINT fk_nv_manager FOREIGN KEY (ma_quan_ly) REFERENCES nhan_vien(ma_nhan_vien),
    CONSTRAINT ck_nhan_vien_luong CHECK (luong>0),
    CONSTRAINT ck_nv_self CHECK (ma_quan_ly IS NULL OR ma_quan_ly<>ma_nhan_vien),
    CONSTRAINT ck_nv_status CHECK (trang_thai IN ('active','inactive')),
    CONSTRAINT ck_nv_phone CHECK (REGEXP_LIKE(so_dien_thoai,'^[+]84[35789][0-9]{8}$'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS tai_khoan (
    ma_tai_khoan VARCHAR(20) PRIMARY KEY,
    ma_nhan_vien VARCHAR(20) NOT NULL UNIQUE,
    mat_khau_hash VARCHAR(255) NULL,
    trang_thai VARCHAR(10) NOT NULL DEFAULT 'locked',
    auth_version INT UNSIGNED NOT NULL DEFAULT 0,
    CONSTRAINT fk_tk_employee FOREIGN KEY (ma_nhan_vien) REFERENCES nhan_vien(ma_nhan_vien),
    CONSTRAINT ck_tk_status CHECK (trang_thai IN ('active','locked','inactive')),
    CONSTRAINT ck_tk_password CHECK (trang_thai<>'active' OR mat_khau_hash IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS chuc_vu (
    ma_chuc_vu VARCHAR(30) PRIMARY KEY,
    ten_chuc_vu VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS vai_tro (
    ma_vai_tro VARCHAR(30) PRIMARY KEY,
    ten_vai_tro VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS quyen (
    ma_quyen VARCHAR(50) PRIMARY KEY,
    mo_ta VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS vai_tro_quyen (
    ma_vai_tro VARCHAR(30) NOT NULL,
    ma_quyen VARCHAR(50) NOT NULL,
    PRIMARY KEY (ma_vai_tro,ma_quyen),
    CONSTRAINT fk_vtq_role FOREIGN KEY (ma_vai_tro) REFERENCES vai_tro(ma_vai_tro),
    CONSTRAINT fk_vtq_permission FOREIGN KEY (ma_quyen) REFERENCES quyen(ma_quyen)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS phan_cong_quyen (
    ma_phan_cong BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ma_tai_khoan VARCHAR(20) NOT NULL,
    ma_vai_tro VARCHAR(30) NOT NULL,
    pham_vi VARCHAR(10) NOT NULL,
    trang_thai VARCHAR(10) NOT NULL DEFAULT 'active',
    ma_khu_vuc INT NULL,
    ma_cua_hang VARCHAR(20) NULL,
    ma_kho VARCHAR(20) NULL,
    tu_ngay DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    den_ngay DATETIME(6) NULL,
    duoc_uy_quyen BOOLEAN NOT NULL DEFAULT FALSE,
    nguoi_cap VARCHAR(20) NULL,
    thu_hoi_luc DATETIME(6) NULL,
    INDEX ix_pcq_active (ma_tai_khoan,thu_hoi_luc,tu_ngay,den_ngay),
    CONSTRAINT fk_pcq_account FOREIGN KEY (ma_tai_khoan) REFERENCES tai_khoan(ma_tai_khoan),
    CONSTRAINT fk_pcq_role FOREIGN KEY (ma_vai_tro) REFERENCES vai_tro(ma_vai_tro),
    CONSTRAINT fk_pcq_region FOREIGN KEY (ma_khu_vuc) REFERENCES khu_vuc(ma_khu_vuc),
    CONSTRAINT fk_pcq_store FOREIGN KEY (ma_cua_hang) REFERENCES cua_hang(ma_cua_hang),
    CONSTRAINT fk_pcq_warehouse FOREIGN KEY (ma_kho) REFERENCES kho(ma_kho),
    CONSTRAINT fk_pcq_issuer FOREIGN KEY (nguoi_cap) REFERENCES tai_khoan(ma_tai_khoan),
    CONSTRAINT ck_pcq_scope CHECK (
        (pham_vi='system' AND ma_khu_vuc IS NULL AND ma_cua_hang IS NULL AND ma_kho IS NULL)
        OR (pham_vi='region' AND ma_khu_vuc IS NOT NULL AND ma_cua_hang IS NULL AND ma_kho IS NULL)
        OR (pham_vi='store' AND ma_khu_vuc IS NULL AND ma_cua_hang IS NOT NULL AND ma_kho IS NULL)
        OR (pham_vi='warehouse' AND ma_khu_vuc IS NULL AND ma_cua_hang IS NULL AND ma_kho IS NOT NULL)),
    CONSTRAINT ck_pcq_time CHECK (den_ngay IS NULL OR den_ngay>tu_ngay),
    CONSTRAINT ck_pcq_delegate CHECK (duoc_uy_quyen IN (0,1)),
    CONSTRAINT ck_pcq_status CHECK (trang_thai IN ('active','pending'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS phan_cong_lam_viec (
    ma_phan_cong BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ma_nhan_vien VARCHAR(20) NOT NULL,
    ma_chuc_vu VARCHAR(30) NOT NULL,
    ma_cua_hang VARCHAR(20) NULL,
    ma_kho VARCHAR(20) NULL,
    tu_ngay DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    den_ngay DATETIME NULL,
    INDEX ix_pclv_active (ma_nhan_vien,tu_ngay,den_ngay),
    CONSTRAINT fk_pclv_employee FOREIGN KEY (ma_nhan_vien) REFERENCES nhan_vien(ma_nhan_vien),
    CONSTRAINT fk_pclv_position FOREIGN KEY (ma_chuc_vu) REFERENCES chuc_vu(ma_chuc_vu),
    CONSTRAINT fk_pclv_store FOREIGN KEY (ma_cua_hang) REFERENCES cua_hang(ma_cua_hang),
    CONSTRAINT fk_pclv_warehouse FOREIGN KEY (ma_kho) REFERENCES kho(ma_kho),
    CONSTRAINT ck_pclv_place CHECK ((ma_cua_hang IS NOT NULL AND ma_kho IS NULL)
        OR (ma_cua_hang IS NULL AND ma_kho IS NOT NULL)),
    CONSTRAINT ck_pclv_time CHECK (den_ngay IS NULL OR den_ngay>tu_ngay)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS danh_muc (
    ma_danh_muc VARCHAR(20) PRIMARY KEY,
    ten_danh_muc VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS mau_san_pham (
    ma_mau VARCHAR(20) PRIMARY KEY,
    ma_danh_muc VARCHAR(20) NOT NULL,
    ten_san_pham VARCHAR(255) NOT NULL,
    trang_thai VARCHAR(10) NOT NULL DEFAULT 'active',
    CONSTRAINT fk_mau_category FOREIGN KEY (ma_danh_muc) REFERENCES danh_muc(ma_danh_muc),
    CONSTRAINT ck_mau_status CHECK (trang_thai IN ('active','inactive'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- san_pham is the existing SKU entity. ma_san_pham is a SKU identifier, not a model ID.
CREATE TABLE IF NOT EXISTS san_pham (
    ma_san_pham VARCHAR(20) PRIMARY KEY,
    ma_mau VARCHAR(20) NOT NULL,
    mau_sac VARCHAR(50) NOT NULL,
    kich_co VARCHAR(20) NOT NULL,
    gia_san_pham DECIMAL(15,2) NOT NULL,
    trang_thai VARCHAR(10) NOT NULL DEFAULT 'active',
    CONSTRAINT uq_san_pham_variant UNIQUE (ma_mau,mau_sac,kich_co),
    CONSTRAINT fk_sp_model FOREIGN KEY (ma_mau) REFERENCES mau_san_pham(ma_mau),
    CONSTRAINT ck_san_pham_gia CHECK (gia_san_pham>=0),
    CONSTRAINT ck_sp_status CHECK (trang_thai IN ('active','inactive'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS ton_kho (
    ma_kho VARCHAR(20) NOT NULL,
    ma_san_pham VARCHAR(20) NOT NULL,
    so_luong INT NOT NULL DEFAULT 0,
    PRIMARY KEY (ma_kho,ma_san_pham),
    CONSTRAINT fk_tk_warehouse FOREIGN KEY (ma_kho) REFERENCES kho(ma_kho),
    CONSTRAINT fk_tk_sku FOREIGN KEY (ma_san_pham) REFERENCES san_pham(ma_san_pham),
    CONSTRAINT ck_ton_kho CHECK (so_luong>=0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS khach_hang (
    ma_khach_hang VARCHAR(20) PRIMARY KEY,
    ho_ten VARCHAR(255) NOT NULL,
    so_dien_thoai VARCHAR(25) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS don_hang (
    ma_don_hang VARCHAR(20) PRIMARY KEY,
    ma_nhan_vien VARCHAR(20) NOT NULL,
    ma_khach_hang VARCHAR(20) NOT NULL,
    ma_cua_hang VARCHAR(20) NOT NULL,
    ma_kho VARCHAR(20) NOT NULL,
    ngay_tao_don DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    trang_thai VARCHAR(15) NOT NULL DEFAULT 'completed',
    INDEX ix_dh_store_date (ma_cua_hang,ngay_tao_don),
    CONSTRAINT fk_dh_employee FOREIGN KEY (ma_nhan_vien) REFERENCES nhan_vien(ma_nhan_vien),
    CONSTRAINT fk_dh_customer FOREIGN KEY (ma_khach_hang) REFERENCES khach_hang(ma_khach_hang),
    CONSTRAINT fk_dh_store FOREIGN KEY (ma_cua_hang) REFERENCES cua_hang(ma_cua_hang),
    CONSTRAINT fk_dh_warehouse_store FOREIGN KEY (ma_kho,ma_cua_hang) REFERENCES kho(ma_kho,ma_cua_hang),
    CONSTRAINT ck_dh_status CHECK (trang_thai IN ('completed','cancelled'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS chi_tiet_don_hang (
    ma_don_hang VARCHAR(20) NOT NULL,
    ma_san_pham VARCHAR(20) NOT NULL,
    so_luong INT NOT NULL,
    don_gia_ban DECIMAL(15,2) NOT NULL,
    giam_gia DECIMAL(15,2) NOT NULL DEFAULT 0,
    PRIMARY KEY (ma_don_hang,ma_san_pham),
    CONSTRAINT fk_ctdh_order FOREIGN KEY (ma_don_hang) REFERENCES don_hang(ma_don_hang),
    CONSTRAINT fk_ctdh_sku FOREIGN KEY (ma_san_pham) REFERENCES san_pham(ma_san_pham),
    CONSTRAINT ck_ctdh_so_luong CHECK (so_luong>0),
    -- Discount is the total discount for this line.
    CONSTRAINT ck_ctdh_don_gia CHECK (don_gia_ban>=0 AND giam_gia>=0
        AND giam_gia<=so_luong*don_gia_ban)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- Distribution is a stock transfer document.
CREATE TABLE IF NOT EXISTS phan_phoi (
    ma_phan_phoi VARCHAR(20) PRIMARY KEY,
    ma_nhan_vien VARCHAR(20) NOT NULL,
    ma_cua_hang VARCHAR(20) NOT NULL,
    ma_kho_nguon VARCHAR(20) NOT NULL,
    ma_kho_dich VARCHAR(20) NOT NULL,
    ngay_phan_phoi DATE NOT NULL,
    trang_thai VARCHAR(15) NOT NULL DEFAULT 'completed',
    CONSTRAINT fk_pp_employee FOREIGN KEY (ma_nhan_vien) REFERENCES nhan_vien(ma_nhan_vien),
    CONSTRAINT fk_pp_store FOREIGN KEY (ma_cua_hang) REFERENCES cua_hang(ma_cua_hang),
    CONSTRAINT fk_pp_source FOREIGN KEY (ma_kho_nguon) REFERENCES kho(ma_kho),
    CONSTRAINT fk_pp_target FOREIGN KEY (ma_kho_dich) REFERENCES kho(ma_kho),
    CONSTRAINT fk_pp_target_store FOREIGN KEY (ma_kho_dich,ma_cua_hang) REFERENCES kho(ma_kho,ma_cua_hang),
    CONSTRAINT ck_pp_status CHECK (trang_thai IN ('completed','cancelled')),
    CONSTRAINT ck_pp_places CHECK (ma_kho_nguon<>ma_kho_dich)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS chi_tiet_phan_phoi (
    ma_phan_phoi VARCHAR(20) NOT NULL,
    ma_san_pham VARCHAR(20) NOT NULL,
    so_luong INT NOT NULL,
    PRIMARY KEY (ma_phan_phoi,ma_san_pham),
    CONSTRAINT fk_ctpp_header FOREIGN KEY (ma_phan_phoi) REFERENCES phan_phoi(ma_phan_phoi),
    CONSTRAINT fk_ctpp_sku FOREIGN KEY (ma_san_pham) REFERENCES san_pham(ma_san_pham),
    CONSTRAINT ck_ctpp_so_luong CHECK (so_luong>0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS bien_dong_kho (
    ma_bien_dong BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ma_kho VARCHAR(20) NOT NULL,
    ma_san_pham VARCHAR(20) NOT NULL,
    so_luong INT NOT NULL,
    loai VARCHAR(15) NOT NULL,
    ly_do VARCHAR(255) NOT NULL,
    ma_tai_khoan VARCHAR(20) NOT NULL,
    ma_don_hang VARCHAR(20) NULL,
    ma_phan_phoi VARCHAR(20) NULL,
    tao_luc DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_bdk_history (ma_kho,ma_san_pham,tao_luc),
    CONSTRAINT fk_bdk_stock FOREIGN KEY (ma_kho,ma_san_pham) REFERENCES ton_kho(ma_kho,ma_san_pham),
    CONSTRAINT fk_bdk_actor FOREIGN KEY (ma_tai_khoan) REFERENCES tai_khoan(ma_tai_khoan),
    CONSTRAINT fk_bdk_order FOREIGN KEY (ma_don_hang) REFERENCES don_hang(ma_don_hang),
    CONSTRAINT fk_bdk_transfer FOREIGN KEY (ma_phan_phoi) REFERENCES phan_phoi(ma_phan_phoi),
    CONSTRAINT ck_bdk_quantity CHECK (so_luong<>0),
    CONSTRAINT ck_bdk_kind CHECK (
        (loai='adjustment' AND ma_don_hang IS NULL AND ma_phan_phoi IS NULL)
        OR (loai IN ('sale','cancel_sale') AND ma_don_hang IS NOT NULL AND ma_phan_phoi IS NULL)
        OR (loai IN ('transfer','cancel_transfer') AND ma_phan_phoi IS NOT NULL AND ma_don_hang IS NULL))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS luot_truy_cap_web (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    thoi_gian DATETIME NOT NULL,
    trang_vao VARCHAR(500) NOT NULL,
    ip_an_danh VARCHAR(64) NOT NULL,
    thiet_bi VARCHAR(10) NOT NULL,
    den_tu VARCHAR(500) NOT NULL,
    INDEX idx_luot_truy_cap_thoi_gian (thoi_gian,id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- @views
-- Read-only projections for the registered academic query library.
-- Installed by the lifecycle runner after tables. Never used to infer authorization.
CREATE OR REPLACE VIEW v_san_pham AS
SELECT s.ma_san_pham,m.ma_danh_muc,m.ten_san_pham,s.mau_sac,s.kich_co,
       s.gia_san_pham,s.gia_san_pham AS gia_ban,s.ma_mau,s.trang_thai
FROM san_pham s JOIN mau_san_pham m ON m.ma_mau=s.ma_mau;
CREATE OR REPLACE VIEW v_nhan_vien AS
SELECT n.ma_nhan_vien,n.ho_ten,n.so_dien_thoai,n.email,n.ma_quan_ly,n.luong,n.trang_thai,lv.ma_cua_hang FROM nhan_vien n LEFT JOIN phan_cong_lam_viec lv
ON lv.ma_phan_cong=(SELECT MAX(l.ma_phan_cong) FROM phan_cong_lam_viec l
WHERE l.ma_nhan_vien=n.ma_nhan_vien AND l.tu_ngay<=UTC_TIMESTAMP()
AND (l.den_ngay IS NULL OR UTC_TIMESTAMP()<l.den_ngay));
CREATE OR REPLACE VIEW v_don_hang AS
SELECT d.* FROM don_hang d WHERE d.trang_thai<>'cancelled';
CREATE OR REPLACE VIEW v_chi_tiet_don_hang AS
SELECT ct.* FROM chi_tiet_don_hang ct JOIN don_hang d ON d.ma_don_hang=ct.ma_don_hang
WHERE d.trang_thai<>'cancelled';
CREATE OR REPLACE VIEW v_phan_phoi AS
SELECT p.* FROM phan_phoi p WHERE p.trang_thai<>'cancelled';
CREATE OR REPLACE VIEW v_chi_tiet_phan_phoi AS
SELECT ct.* FROM chi_tiet_phan_phoi ct JOIN phan_phoi p ON p.ma_phan_phoi=ct.ma_phan_phoi
WHERE p.trang_thai<>'cancelled';

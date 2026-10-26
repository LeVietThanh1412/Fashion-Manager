-- MySQL 8.0.31+. TAO MOI DATABASE DEMO: lenh DROP se xoa database cung ten.
-- Neu da co du lieu, chi chay 4.CapNhatPhanQuyen.sql.
DROP DATABASE IF EXISTS quan_ly_chuoi_thoi_trang;
CREATE DATABASE quan_ly_chuoi_thoi_trang CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE quan_ly_chuoi_thoi_trang;

CREATE TABLE danh_muc (
    ma_danh_muc VARCHAR(20) PRIMARY KEY,
    ten_danh_muc VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE san_pham (
    ma_san_pham VARCHAR(20) PRIMARY KEY,
    ma_danh_muc VARCHAR(20) NOT NULL,
    ten_san_pham VARCHAR(255) NOT NULL,
    mau_sac VARCHAR(50) NOT NULL,
    kich_co VARCHAR(20) NOT NULL,
    gia_san_pham DECIMAL(15,0) NOT NULL,
    CONSTRAINT uq_bien_the UNIQUE (ten_san_pham,mau_sac,kich_co),
    CONSTRAINT ck_gia_san_pham CHECK (gia_san_pham >= 0),
    FOREIGN KEY (ma_danh_muc) REFERENCES danh_muc(ma_danh_muc)
) ENGINE=InnoDB;

CREATE TABLE cua_hang (
    ma_cua_hang VARCHAR(20) PRIMARY KEY,
    ten_cua_hang VARCHAR(255) NOT NULL,
    khu_vuc TINYINT NOT NULL COMMENT '1: Mien Bac, 2: Mien Trung, 3: Mien Nam',
    dia_chi VARCHAR(255) NOT NULL,
    so_dien_thoai VARCHAR(25) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    CONSTRAINT ck_cua_hang_khu_vuc CHECK (khu_vuc IN (1,2,3))
) ENGINE=InnoDB;

CREATE TABLE nhan_vien (
    ma_nhan_vien VARCHAR(20) PRIMARY KEY,
    ho_ten VARCHAR(255) NOT NULL,
    so_dien_thoai VARCHAR(25) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    ma_cua_hang VARCHAR(20),
    ma_quan_ly VARCHAR(20),
    quyen_han ENUM('admin','regional_manager','store_manager','staff') NOT NULL DEFAULT 'staff',
    khu_vuc_quan_ly TINYINT,
    luong DECIMAL(12,2) NOT NULL DEFAULT 0,
    cap_bac TINYINT NOT NULL DEFAULT 2 COMMENT '1: Thu viec, 2: Chinh thuc, 3: Truong ca',
    trang_thai ENUM('active','inactive') NOT NULL DEFAULT 'active',
    FOREIGN KEY (ma_cua_hang) REFERENCES cua_hang(ma_cua_hang),
    FOREIGN KEY (ma_quan_ly) REFERENCES nhan_vien(ma_nhan_vien),
    CONSTRAINT ck_luong CHECK (luong >= 0),
    CONSTRAINT ck_cap_bac CHECK (cap_bac BETWEEN 1 AND 3),
    CONSTRAINT ck_pham_vi CHECK (
        (quyen_han='admin' AND ma_cua_hang IS NULL AND khu_vuc_quan_ly IS NULL)
        OR (quyen_han='regional_manager' AND ma_cua_hang IS NULL AND khu_vuc_quan_ly IS NOT NULL AND khu_vuc_quan_ly IN (1,2,3))
        OR (quyen_han IN ('store_manager','staff') AND ma_cua_hang IS NOT NULL AND khu_vuc_quan_ly IS NULL)
    )
) ENGINE=InnoDB;

-- UNIQUE tren bieu thuc: chi nguoi dang giu chuc vu moi chiem vi tri.
-- Nguoi da nghi/historic tra ve NULL nen khong can them cot du thua.
CREATE UNIQUE INDEX uq_mot_chu_thuong_hieu ON nhan_vien
    ((CASE WHEN quyen_han='admin' AND trang_thai='active' THEN 1 ELSE NULL END));
CREATE UNIQUE INDEX uq_quan_ly_khu_vuc ON nhan_vien
    ((CASE WHEN quyen_han='regional_manager' AND trang_thai='active' THEN khu_vuc_quan_ly ELSE NULL END));
CREATE UNIQUE INDEX uq_quan_ly_cua_hang ON nhan_vien
    ((CASE WHEN quyen_han='store_manager' AND trang_thai='active' THEN ma_cua_hang ELSE NULL END));

CREATE TABLE phan_phoi (
    ma_phan_phoi VARCHAR(20) PRIMARY KEY,
    ngay_phan_phoi DATE NOT NULL,
    ma_nhan_vien VARCHAR(20) NOT NULL,
    FOREIGN KEY (ma_nhan_vien) REFERENCES nhan_vien(ma_nhan_vien)
) ENGINE=InnoDB;

CREATE TABLE chi_tiet_phan_phoi (
    ma_phan_phoi VARCHAR(20) NOT NULL,
    ma_san_pham VARCHAR(20) NOT NULL,
    so_luong INT NOT NULL,
    PRIMARY KEY (ma_phan_phoi,ma_san_pham),
    CONSTRAINT ck_so_luong_phan_phoi CHECK (so_luong > 0),
    FOREIGN KEY (ma_phan_phoi) REFERENCES phan_phoi(ma_phan_phoi),
    FOREIGN KEY (ma_san_pham) REFERENCES san_pham(ma_san_pham)
) ENGINE=InnoDB;

CREATE TABLE khach_hang (
    ma_khach_hang VARCHAR(20) PRIMARY KEY,
    ho_ten VARCHAR(255) NOT NULL,
    so_dien_thoai VARCHAR(25) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE don_hang (
    ma_don_hang VARCHAR(20) PRIMARY KEY,
    ma_nhan_vien VARCHAR(20) NOT NULL,
    ma_khach_hang VARCHAR(20) NOT NULL,
    ngay_tao_don DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ma_nhan_vien) REFERENCES nhan_vien(ma_nhan_vien),
    FOREIGN KEY (ma_khach_hang) REFERENCES khach_hang(ma_khach_hang)
) ENGINE=InnoDB;

-- Gia tai thoi diem ban; khong phai ban sao gia hien hanh cua san_pham.
-- Thanh tien va tong tien duoc tinh bang SELECT, khong luu lap lai.
CREATE TABLE chi_tiet_don_hang (
    ma_don_hang VARCHAR(20) NOT NULL,
    ma_san_pham VARCHAR(20) NOT NULL,
    so_luong INT NOT NULL,
    don_gia_ban DECIMAL(15,0) NOT NULL,
    PRIMARY KEY (ma_don_hang,ma_san_pham),
    CONSTRAINT ck_so_luong_mua CHECK (so_luong > 0),
    CONSTRAINT ck_don_gia_ban CHECK (don_gia_ban >= 0),
    FOREIGN KEY (ma_don_hang) REFERENCES don_hang(ma_don_hang),
    FOREIGN KEY (ma_san_pham) REFERENCES san_pham(ma_san_pham)
) ENGINE=InnoDB;

-- Luu cac lan bo nhiem; moi lan la mot su kien rieng, khong lap ten nhan vien/cua hang.
CREATE TABLE lich_su_quan_ly (
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

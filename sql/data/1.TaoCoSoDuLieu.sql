-- Tao co so du lieu quan ly chuoi cua hang thoi trang
DROP DATABASE IF EXISTS quan_ly_chuoi_thoi_trang;
CREATE DATABASE quan_ly_chuoi_thoi_trang;
USE quan_ly_chuoi_thoi_trang;

-- Bang danh muc
DROP TABLE IF EXISTS danh_muc;
CREATE TABLE danh_muc (
    ma_danh_muc VARCHAR(20) PRIMARY KEY,
    ten_danh_muc VARCHAR(255) NOT NULL UNIQUE
);

-- Bang san pham
DROP TABLE IF EXISTS san_pham;
CREATE TABLE san_pham (
    ma_san_pham VARCHAR(20) PRIMARY KEY,
    ma_danh_muc VARCHAR(20) NOT NULL,
    ten_san_pham VARCHAR(255) NOT NULL,
    mau_sac VARCHAR(50) NOT NULL,
    kich_co VARCHAR(20) NOT NULL,
    gia_ban DECIMAL(15,0) NOT NULL,

    UNIQUE (ten_san_pham, mau_sac, kich_co),
    CHECK (gia_ban >= 0),

    FOREIGN KEY (ma_danh_muc)
        REFERENCES danh_muc(ma_danh_muc)
);

-- Bang cua hang
DROP TABLE IF EXISTS cua_hang;
CREATE TABLE cua_hang (
    ma_cua_hang VARCHAR(20) PRIMARY KEY,
    ten_cua_hang VARCHAR(255) NOT NULL,
    dia_chi VARCHAR(255) NOT NULL,
    so_dien_thoai VARCHAR(25) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE
);

-- Bang nhan vien
DROP TABLE IF EXISTS nhan_vien;
CREATE TABLE nhan_vien (
    ma_nhan_vien VARCHAR(20) PRIMARY KEY,
    ho_ten VARCHAR(255) NOT NULL,
    so_dien_thoai VARCHAR(25) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    ma_cua_hang VARCHAR(20),
    ma_quan_ly VARCHAR(20),

    FOREIGN KEY (ma_cua_hang)
        REFERENCES cua_hang(ma_cua_hang),

    FOREIGN KEY (ma_quan_ly)
        REFERENCES nhan_vien(ma_nhan_vien)
);

-- Bang phieu phan phoi
DROP TABLE IF EXISTS phan_phoi;
CREATE TABLE phan_phoi (
    ma_phan_phoi VARCHAR(20) PRIMARY KEY,
    ma_cua_hang VARCHAR(20) NOT NULL,
    ngay_phan_phoi DATE NOT NULL,
    ma_nhan_vien VARCHAR(20) NOT NULL,

    FOREIGN KEY (ma_cua_hang)
        REFERENCES cua_hang(ma_cua_hang),

    FOREIGN KEY (ma_nhan_vien)
        REFERENCES nhan_vien(ma_nhan_vien)
);

-- Bang chi tiet phieu phan phoi
CREATE TABLE chi_tiet_phan_phoi (
    ma_phan_phoi VARCHAR(20) NOT NULL,
    ma_san_pham VARCHAR(20) NOT NULL,
    so_luong INT NOT NULL,

    PRIMARY KEY (ma_phan_phoi, ma_san_pham),
    CHECK (so_luong > 0),

    FOREIGN KEY (ma_phan_phoi)
        REFERENCES phan_phoi(ma_phan_phoi),

    FOREIGN KEY (ma_san_pham)
        REFERENCES san_pham(ma_san_pham)
);

-- Bang khach hang
DROP TABLE IF EXISTS khach_hang;
CREATE TABLE khach_hang (
    ma_khach_hang VARCHAR(20) PRIMARY KEY,
    ho_ten VARCHAR(255) NOT NULL,
    so_dien_thoai VARCHAR(25) NOT NULL UNIQUE
);

DROP TABLE IF EXISTS don_hang;
CREATE TABLE don_hang (
    ma_don_hang VARCHAR(20) PRIMARY KEY,
    ma_nhan_vien VARCHAR(20) NOT NULL,
    ma_khach_hang VARCHAR(20) NOT NULL,
    ngay_tao_don DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (ma_nhan_vien)
        REFERENCES nhan_vien(ma_nhan_vien),

    FOREIGN KEY (ma_khach_hang)
        REFERENCES khach_hang(ma_khach_hang)
);

-- Bang chi tiet don hang
DROP TABLE IF EXISTS chi_tiet_don_hang;
CREATE TABLE chi_tiet_don_hang (
    ma_chi_tiet VARCHAR(20) PRIMARY KEY,
    ma_don_hang VARCHAR(20) NOT NULL,
    ma_san_pham VARCHAR(20) NOT NULL,
    so_luong INT NOT NULL,
    don_gia_ban DECIMAL(15,0) NOT NULL,

    UNIQUE (ma_don_hang, ma_san_pham),
    CHECK (so_luong > 0),
    CHECK (don_gia_ban >= 0),

    FOREIGN KEY (ma_don_hang)
        REFERENCES don_hang(ma_don_hang),

    FOREIGN KEY (ma_san_pham)
        REFERENCES san_pham(ma_san_pham)
);
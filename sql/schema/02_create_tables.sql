USE quan_ly_chuoi_thoi_trang;

CREATE TABLE danh_muc (
    ma_danh_muc VARCHAR(20) PRIMARY KEY,
    ten_danh_muc VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE cua_hang (
    ma_cua_hang VARCHAR(20) PRIMARY KEY,
    ten_cua_hang VARCHAR(255) NOT NULL,
    dia_chi VARCHAR(255) NOT NULL,
    so_dien_thoai VARCHAR(25) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE san_pham (
    ma_san_pham VARCHAR(20) PRIMARY KEY,
    ma_danh_muc VARCHAR(20) NOT NULL,
    ten_san_pham VARCHAR(255) NOT NULL,
    mau_sac VARCHAR(50) NOT NULL,
    kich_co VARCHAR(20) NOT NULL,
    gia_ban DECIMAL(15,0) NOT NULL,
    CONSTRAINT uq_san_pham_variant UNIQUE (ten_san_pham, mau_sac, kich_co),
    CONSTRAINT ck_san_pham_gia CHECK (gia_ban >= 0),
    CONSTRAINT fk_san_pham_danh_muc FOREIGN KEY (ma_danh_muc)
        REFERENCES danh_muc(ma_danh_muc)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE nhan_vien (
    ma_nhan_vien VARCHAR(20) PRIMARY KEY,
    ho_ten VARCHAR(255) NOT NULL,
    so_dien_thoai VARCHAR(25) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    ma_cua_hang VARCHAR(20) NOT NULL,
    ma_quan_ly VARCHAR(20),
    CONSTRAINT fk_nhan_vien_cua_hang FOREIGN KEY (ma_cua_hang)
        REFERENCES cua_hang(ma_cua_hang),
    CONSTRAINT fk_nhan_vien_quan_ly FOREIGN KEY (ma_quan_ly)
        REFERENCES nhan_vien(ma_nhan_vien)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE phan_phoi (
    ma_phan_phoi VARCHAR(20) PRIMARY KEY,
    ma_cua_hang VARCHAR(20) NOT NULL,
    ngay_phan_phoi DATE NOT NULL,
    ma_nhan_vien VARCHAR(20) NOT NULL,
    CONSTRAINT fk_phan_phoi_cua_hang FOREIGN KEY (ma_cua_hang)
        REFERENCES cua_hang(ma_cua_hang),
    CONSTRAINT fk_phan_phoi_nhan_vien FOREIGN KEY (ma_nhan_vien)
        REFERENCES nhan_vien(ma_nhan_vien)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE chi_tiet_phan_phoi (
    ma_phan_phoi VARCHAR(20) NOT NULL,
    ma_san_pham VARCHAR(20) NOT NULL,
    so_luong INT NOT NULL,
    PRIMARY KEY (ma_phan_phoi, ma_san_pham),
    CONSTRAINT ck_ctpp_so_luong CHECK (so_luong > 0),
    CONSTRAINT fk_ctpp_phan_phoi FOREIGN KEY (ma_phan_phoi)
        REFERENCES phan_phoi(ma_phan_phoi),
    CONSTRAINT fk_ctpp_san_pham FOREIGN KEY (ma_san_pham)
        REFERENCES san_pham(ma_san_pham)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE khach_hang (
    ma_khach_hang VARCHAR(20) PRIMARY KEY,
    ho_ten VARCHAR(255) NOT NULL,
    so_dien_thoai VARCHAR(25) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE don_hang (
    ma_don_hang VARCHAR(20) PRIMARY KEY,
    ma_nhan_vien VARCHAR(20) NOT NULL,
    ma_khach_hang VARCHAR(20) NOT NULL,
    ngay_tao_don DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_don_hang_nhan_vien FOREIGN KEY (ma_nhan_vien)
        REFERENCES nhan_vien(ma_nhan_vien),
    CONSTRAINT fk_don_hang_khach_hang FOREIGN KEY (ma_khach_hang)
        REFERENCES khach_hang(ma_khach_hang)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE chi_tiet_don_hang (
    ma_chi_tiet VARCHAR(20) PRIMARY KEY,
    ma_don_hang VARCHAR(20) NOT NULL,
    ma_san_pham VARCHAR(20) NOT NULL,
    so_luong INT NOT NULL,
    don_gia_ban DECIMAL(15,0) NOT NULL,
    CONSTRAINT uq_ctdh_don_san_pham UNIQUE (ma_don_hang, ma_san_pham),
    CONSTRAINT ck_ctdh_so_luong CHECK (so_luong > 0),
    CONSTRAINT ck_ctdh_don_gia CHECK (don_gia_ban >= 0),
    CONSTRAINT fk_ctdh_don_hang FOREIGN KEY (ma_don_hang)
        REFERENCES don_hang(ma_don_hang),
    CONSTRAINT fk_ctdh_san_pham FOREIGN KEY (ma_san_pham)
        REFERENCES san_pham(ma_san_pham)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tao co so du lieu quan ly chuoi cua hang thoi trang
drop database if exists quan_ly_chuoi_thoi_trang;
CREATE database quan_ly_chuoi_thoi_trang;
USE quan_ly_chuoi_thoi_trang;

-- Bang danh muc
drop table if exists danh_muc;
create table danh_muc (
    ma_danh_muc varchar(20)primary key,
    ten_danh_muc varchar(255) not null unique
);

-- Bang san pham
drop table if exists san_pham;
create table san_pham (
    ma_san_pham varchar(20)primary key,
    ma_danh_muc varchar(20) not null,
    ten_san_pham varchar(255) not null,
    mau_sac varchar(50) not null,
    kich_co varchar(20) not null,
    gia_san_pham DECIMAL(15,0) not null,

    unique (ten_san_pham, mau_sac, kich_co),
    check (gia_san_pham >= 0),

    foreign key (ma_danh_muc)
        references danh_muc(ma_danh_muc)
);

-- Bang cua hang
drop table if exists cua_hang;
create table cua_hang (
    ma_cua_hang varchar(20)primary key,
    ten_cua_hang varchar(255) not null,
    khu_vuc TINYINT not null check (khu_vuc IN (1, 2, 3)),
    dia_chi varchar(255) not null,
    so_dien_thoai varchar(25) not null unique,
    email varchar(255) not null unique
);

-- Bang nhan vien
drop table if exists nhan_vien;
create table nhan_vien (
    ma_nhan_vien varchar(20)primary key,
    ho_ten varchar(255) not null,
    so_dien_thoai varchar(25) not null unique,
    email varchar(255) not null unique,
    ma_cua_hang varchar(20),
    ma_quan_ly varchar(20),
    luong DECIMAL(15,0) not null,

    foreign key (ma_cua_hang)
        references cua_hang(ma_cua_hang),

    foreign key (ma_quan_ly)
        references nhan_vien(ma_nhan_vien),

    check (luong > 0)
);

-- Bang phieu phan phoi
drop table if exists phan_phoi;
create table phan_phoi (
    ma_phan_phoi varchar(20)primary key,
    ngay_phan_phoi DATE not null,
    ma_nhan_vien varchar(20) not null,

    foreign key (ma_nhan_vien)
        references nhan_vien(ma_nhan_vien)
);

-- Bang chi tiet phieu phan phoi
drop table if exists chi_tiet_phan_phoi;
create table chi_tiet_phan_phoi (
    ma_phan_phoi varchar(20) not null,
    ma_san_pham varchar(20) not null,
    so_luong INT not null,

   primary key (ma_phan_phoi, ma_san_pham),
    check (so_luong > 0),

    foreign key (ma_phan_phoi)
        references phan_phoi(ma_phan_phoi),

    foreign key (ma_san_pham)
        references san_pham(ma_san_pham)
);

-- Bang khach hang
drop table if exists khach_hang;
create table khach_hang (
    ma_khach_hang varchar(20)primary key,
    ho_ten varchar(255) not null,
    so_dien_thoai varchar(25) not null unique
);

drop table if exists don_hang;
create table don_hang (
    ma_don_hang varchar(20)primary key,
    ma_nhan_vien varchar(20) not null,
    ma_khach_hang varchar(20) not null,
    ngay_tao_don DATETIME not null DEFAULT CURRENT_TIMESTAMP,

    foreign key (ma_nhan_vien)
        references nhan_vien(ma_nhan_vien),

    foreign key (ma_khach_hang)
        references khach_hang(ma_khach_hang)
);

-- Bang chi tiet don hang
drop table if exists chi_tiet_don_hang;

create table chi_tiet_don_hang (
    ma_don_hang varchar(20) not null,
    ma_san_pham varchar(20) not null,
    so_luong INT not null,

    unique (ma_don_hang, ma_san_pham),
    check (so_luong > 0),

   primary key (ma_don_hang, ma_san_pham),

    foreign key (ma_don_hang)
        references don_hang(ma_don_hang),

    foreign key (ma_san_pham)
        references san_pham(ma_san_pham)
);
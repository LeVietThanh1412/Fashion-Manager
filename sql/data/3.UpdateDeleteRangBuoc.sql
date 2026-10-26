USE quan_ly_chuoi_thoi_trang;

-- Chay mot lan sau khi tao schema cua hang co cot khu_vuc va nap du lieu.
-- Quy uoc ma khu vuc: 1 = Mien Bac, 2 = Mien Trung, 3 = Mien Nam.
-- Script khong xoa du lieu; nhan vien cu mac dinh duoc gan vai tro nhan_vien.

-- Chuan hoa hai cot legacy de cac truy van backend dung chung schema 02.
CREATE TABLE IF NOT EXISTS khu_vuc (
    ma_khu_vuc TINYINT PRIMARY KEY,
    ten_khu_vuc VARCHAR(30) NOT NULL UNIQUE,
    CHECK (ma_khu_vuc IN (1, 2, 3))
);

INSERT IGNORE INTO khu_vuc (ma_khu_vuc, ten_khu_vuc) VALUES
    (1, 'Miền Bắc'),
    (2, 'Miền Trung'),
    (3, 'Miền Nam');

ALTER TABLE cua_hang
    ADD FOREIGN KEY (khu_vuc) REFERENCES khu_vuc(ma_khu_vuc);

ALTER TABLE nhan_vien
    ADD COLUMN quyen_han ENUM(
        'quan_ly',
        'quan_ly_khu_vuc',
        'quan_ly_cua_hang',
        'nhan_vien'
    ) NOT NULL DEFAULT 'nhan_vien',
    ADD COLUMN khu_vuc_quan_ly TINYINT NULL;

-- Gan vai tro cho bo du lieu mau:
-- NV000 la quan_ly; NV001-NV003 la quan ly khu vuc.
-- Nhan vien co nhan vien cap duoi va co cua hang la quan ly cua hang.
UPDATE nhan_vien AS nv
LEFT JOIN (
    SELECT ma_quan_ly, COUNT(*) AS so_cap_duoi
    FROM nhan_vien
    WHERE ma_quan_ly IS NOT NULL
    GROUP BY ma_quan_ly
) AS danh_sach_quan_ly
    ON danh_sach_quan_ly.ma_quan_ly = nv.ma_nhan_vien
SET nv.quyen_han = CASE
        WHEN nv.ma_nhan_vien = 'NV000' THEN 'quan_ly'
        WHEN nv.ma_nhan_vien IN ('NV001', 'NV002', 'NV003') THEN 'quan_ly_khu_vuc'
        WHEN nv.ma_cua_hang IS NOT NULL
             AND danh_sach_quan_ly.so_cap_duoi IS NOT NULL THEN 'quan_ly_cua_hang'
        ELSE 'nhan_vien'
    END;

UPDATE nhan_vien
SET khu_vuc_quan_ly = CASE ma_nhan_vien
    WHEN 'NV001' THEN 1
    WHEN 'NV002' THEN 2
    WHEN 'NV003' THEN 3
END
WHERE quyen_han = 'quan_ly_khu_vuc'
  AND ma_nhan_vien IN ('NV001', 'NV002', 'NV003');

ALTER TABLE nhan_vien
    ADD FOREIGN KEY (khu_vuc_quan_ly) REFERENCES khu_vuc(ma_khu_vuc),
    ADD CHECK (
            (quyen_han = 'quan_ly'
                AND ma_cua_hang IS NULL
                AND khu_vuc_quan_ly IS NULL)
            OR
            (quyen_han = 'quan_ly_khu_vuc'
                AND ma_cua_hang IS NULL
                AND khu_vuc_quan_ly IS NOT NULL)
            OR
            (quyen_han IN ('quan_ly_cua_hang', 'nhan_vien')
                AND ma_cua_hang IS NOT NULL
                AND khu_vuc_quan_ly IS NULL)
        );

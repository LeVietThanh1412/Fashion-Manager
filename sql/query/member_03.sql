-- Query ID: M03_Q01
-- Title: Phan phoi va san pham 1
-- Level: 1 - basic
-- Tables: phan_phoi,chi_tiet_phan_phoi,san_pham
-- Techniques: JOIN, WHERE
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT p.ma_san_pham,p.ten_san_pham,ct.so_luong FROM chi_tiet_phan_phoi ct JOIN san_pham p ON p.ma_san_pham=ct.ma_san_pham WHERE ct.so_luong>20 ORDER BY ct.so_luong DESC;


-- Query ID: M03_Q02
-- Title: Phieu phan phoi theo ngay gan nhat
-- Level: 1 - basic
SELECT ma_phan_phoi,ngay_phan_phoi,ma_nhan_vien FROM phan_phoi ORDER BY ngay_phan_phoi DESC,ma_phan_phoi;

-- Query ID: M03_Q03
-- Title: Phan phoi va san pham 3
-- Level: 1 - basic
-- Tables: phan_phoi,chi_tiet_phan_phoi,san_pham
-- Techniques: JOIN, GROUP BY
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT pp.ma_phan_phoi,pp.ngay_phan_phoi,SUM(ct.so_luong) AS tong_so_luong FROM phan_phoi pp JOIN chi_tiet_phan_phoi ct ON ct.ma_phan_phoi=pp.ma_phan_phoi WHERE pp.ngay_phan_phoi BETWEEN '2026-01-01' AND '2026-12-31' GROUP BY pp.ma_phan_phoi,pp.ngay_phan_phoi ORDER BY pp.ngay_phan_phoi;


-- Query ID: M03_Q04
-- Title: Phieu phan phoi va nguoi nhan tai cua hang
-- Level: 2 - join
SELECT pp.ma_phan_phoi,nv.ho_ten AS nguoi_nhan,ch.ten_cua_hang FROM phan_phoi pp JOIN nhan_vien nv ON nv.ma_nhan_vien=pp.ma_nhan_vien JOIN cua_hang ch ON ch.ma_cua_hang=nv.ma_cua_hang ORDER BY pp.ma_phan_phoi;

-- Query ID: M03_Q05
-- Title: Chi tiet san pham cua phieu PP001
-- Level: 2 - join
SELECT ct.ma_san_pham,sp.ten_san_pham,sp.mau_sac,sp.kich_co,ct.so_luong FROM chi_tiet_phan_phoi ct JOIN san_pham sp ON sp.ma_san_pham=ct.ma_san_pham WHERE ct.ma_phan_phoi='PP001' ORDER BY ct.ma_san_pham;

-- Query ID: M03_Q06
-- Title: So phieu phan phoi theo thang
-- Level: 3 - aggregate/subquery
SELECT YEAR(ngay_phan_phoi) AS nam,MONTH(ngay_phan_phoi) AS thang,COUNT(*) AS so_phieu FROM phan_phoi GROUP BY YEAR(ngay_phan_phoi),MONTH(ngay_phan_phoi) ORDER BY nam,thang;

-- Query ID: M03_Q07
-- Title: Tong so luong phan phoi tung san pham
-- Level: 3 - aggregate/subquery
SELECT sp.ma_san_pham,sp.ten_san_pham,SUM(ct.so_luong) AS tong_phan_phoi FROM san_pham sp JOIN chi_tiet_phan_phoi ct ON ct.ma_san_pham=sp.ma_san_pham GROUP BY sp.ma_san_pham,sp.ten_san_pham ORDER BY tong_phan_phoi DESC;

-- Query ID: M03_Q08
-- Title: Thong ke phan phoi theo cua hang
-- Level: 3 - aggregate/subquery
SELECT ch.ma_cua_hang,ch.ten_cua_hang,COUNT(DISTINCT pp.ma_phan_phoi) AS so_phieu,SUM(ct.so_luong) AS tong_nhan FROM cua_hang ch JOIN nhan_vien nv ON nv.ma_cua_hang=ch.ma_cua_hang JOIN phan_phoi pp ON pp.ma_nhan_vien=nv.ma_nhan_vien JOIN chi_tiet_phan_phoi ct ON ct.ma_phan_phoi=pp.ma_phan_phoi GROUP BY ch.ma_cua_hang,ch.ten_cua_hang ORDER BY ch.ma_cua_hang;

-- Query ID: M03_Q09
-- Title: Nhan vien nhan it nhat hai phieu
-- Level: 3 - aggregate/subquery
SELECT nv.ma_nhan_vien,nv.ho_ten,COUNT(pp.ma_phan_phoi) AS so_phieu_nhan FROM nhan_vien nv JOIN phan_phoi pp ON pp.ma_nhan_vien=nv.ma_nhan_vien GROUP BY nv.ma_nhan_vien,nv.ho_ten HAVING COUNT(pp.ma_phan_phoi)>=2 ORDER BY so_phieu_nhan DESC;

-- Query ID: M03_Q10
-- Title: San pham chua duoc phan phoi
-- Level: 3 - aggregate/subquery
SELECT sp.ma_san_pham,sp.ten_san_pham FROM san_pham sp WHERE NOT EXISTS (SELECT 1 FROM chi_tiet_phan_phoi ct WHERE ct.ma_san_pham=sp.ma_san_pham) ORDER BY sp.ma_san_pham;


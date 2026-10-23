-- Query ID: M03_Q01
-- Title: Phan phoi va san pham 1
-- Level: 1 - basic
-- Tables: phan_phoi,chi_tiet_phan_phoi,san_pham
-- Techniques: JOIN, WHERE
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT p.ma_san_pham,p.ten_san_pham,ct.so_luong FROM chi_tiet_phan_phoi ct JOIN san_pham p ON p.ma_san_pham=ct.ma_san_pham WHERE ct.so_luong>20 ORDER BY ct.so_luong DESC;


-- Query ID: M03_Q02
-- Title: Phan phoi va san pham 2
-- Level: 1 - basic
-- Tables: phan_phoi,chi_tiet_phan_phoi,san_pham
-- Techniques: JOIN, WHERE
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT p.ma_san_pham,p.ten_san_pham,ct.so_luong FROM chi_tiet_phan_phoi ct JOIN san_pham p ON p.ma_san_pham=ct.ma_san_pham WHERE ct.so_luong>20 ORDER BY ct.so_luong DESC;


-- Query ID: M03_Q03
-- Title: Phan phoi va san pham 3
-- Level: 1 - basic
-- Tables: phan_phoi,chi_tiet_phan_phoi,san_pham
-- Techniques: JOIN, GROUP BY
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT pp.ma_phan_phoi,pp.ngay_phan_phoi,SUM(ct.so_luong) AS tong_so_luong FROM phan_phoi pp JOIN chi_tiet_phan_phoi ct ON ct.ma_phan_phoi=pp.ma_phan_phoi WHERE pp.ngay_phan_phoi BETWEEN '2026-01-01' AND '2026-12-31' GROUP BY pp.ma_phan_phoi,pp.ngay_phan_phoi ORDER BY pp.ngay_phan_phoi;


-- Query ID: M03_Q04
-- Title: Phan phoi va san pham 4
-- Level: 1 - basic
-- Tables: phan_phoi,chi_tiet_phan_phoi,san_pham
-- Techniques: JOIN, WHERE
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT p.ma_san_pham,p.ten_san_pham,ct.so_luong FROM chi_tiet_phan_phoi ct JOIN san_pham p ON p.ma_san_pham=ct.ma_san_pham WHERE ct.so_luong>20 ORDER BY ct.so_luong DESC;


-- Query ID: M03_Q05
-- Title: Phan phoi va san pham 5
-- Level: 2 - join
-- Tables: phan_phoi,chi_tiet_phan_phoi,san_pham
-- Techniques: JOIN, WHERE
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT p.ma_san_pham,p.ten_san_pham,ct.so_luong FROM chi_tiet_phan_phoi ct JOIN san_pham p ON p.ma_san_pham=ct.ma_san_pham WHERE ct.so_luong>20 ORDER BY ct.so_luong DESC;


-- Query ID: M03_Q06
-- Title: Phan phoi va san pham 6
-- Level: 2 - join
-- Tables: phan_phoi,chi_tiet_phan_phoi,san_pham
-- Techniques: JOIN, GROUP BY
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT pp.ma_phan_phoi,pp.ngay_phan_phoi,SUM(ct.so_luong) AS tong_so_luong FROM phan_phoi pp JOIN chi_tiet_phan_phoi ct ON ct.ma_phan_phoi=pp.ma_phan_phoi WHERE pp.ngay_phan_phoi BETWEEN '2026-01-01' AND '2026-12-31' GROUP BY pp.ma_phan_phoi,pp.ngay_phan_phoi ORDER BY pp.ngay_phan_phoi;


-- Query ID: M03_Q07
-- Title: Phan phoi va san pham 7
-- Level: 2 - join
-- Tables: phan_phoi,chi_tiet_phan_phoi,san_pham
-- Techniques: JOIN, WHERE
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT p.ma_san_pham,p.ten_san_pham,ct.so_luong FROM chi_tiet_phan_phoi ct JOIN san_pham p ON p.ma_san_pham=ct.ma_san_pham WHERE ct.so_luong>20 ORDER BY ct.so_luong DESC;


-- Query ID: M03_Q08
-- Title: Phan phoi va san pham 8
-- Level: 3 - aggregate/subquery
-- Tables: phan_phoi,chi_tiet_phan_phoi,san_pham
-- Techniques: JOIN, WHERE
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT p.ma_san_pham,p.ten_san_pham,ct.so_luong FROM chi_tiet_phan_phoi ct JOIN san_pham p ON p.ma_san_pham=ct.ma_san_pham WHERE ct.so_luong>20 ORDER BY ct.so_luong DESC;


-- Query ID: M03_Q09
-- Title: Phan phoi va san pham 9
-- Level: 3 - aggregate/subquery
-- Tables: phan_phoi,chi_tiet_phan_phoi,san_pham
-- Techniques: JOIN, GROUP BY
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT pp.ma_phan_phoi,pp.ngay_phan_phoi,SUM(ct.so_luong) AS tong_so_luong FROM phan_phoi pp JOIN chi_tiet_phan_phoi ct ON ct.ma_phan_phoi=pp.ma_phan_phoi WHERE pp.ngay_phan_phoi BETWEEN '2026-01-01' AND '2026-12-31' GROUP BY pp.ma_phan_phoi,pp.ngay_phan_phoi ORDER BY pp.ngay_phan_phoi;


-- Query ID: M03_Q10
-- Title: Phan phoi va san pham 10
-- Level: 3 - aggregate/subquery
-- Tables: phan_phoi,chi_tiet_phan_phoi,san_pham
-- Techniques: JOIN, WHERE
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT p.ma_san_pham,p.ten_san_pham,ct.so_luong FROM chi_tiet_phan_phoi ct JOIN san_pham p ON p.ma_san_pham=ct.ma_san_pham WHERE ct.so_luong>20 ORDER BY ct.so_luong DESC;


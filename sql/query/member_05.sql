-- Query ID: M05_Q01
-- Title: Bao cao tong hop 1
-- Level: 1 - basic
-- Tables: san_pham,chi_tiet_don_hang,chi_tiet_phan_phoi
-- Techniques: UNION
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT ma_san_pham FROM san_pham WHERE gia_ban=0 UNION SELECT ma_san_pham FROM san_pham WHERE kich_co='XL';


-- Query ID: M05_Q02
-- Title: Bao cao tong hop 2
-- Level: 1 - basic
-- Tables: san_pham,chi_tiet_don_hang,chi_tiet_phan_phoi
-- Techniques: INTERSECT
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT ma_san_pham FROM san_pham WHERE gia_ban>200000 INTERSECT SELECT ma_san_pham FROM san_pham WHERE kich_co IN ('L','XL');


-- Query ID: M05_Q03
-- Title: Bao cao tong hop 3
-- Level: 1 - basic
-- Tables: san_pham,chi_tiet_don_hang,chi_tiet_phan_phoi
-- Techniques: EXCEPT
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT ma_san_pham FROM san_pham EXCEPT SELECT ma_san_pham FROM chi_tiet_don_hang;


-- Query ID: M05_Q04
-- Title: Bao cao tong hop 4
-- Level: 1 - basic
-- Tables: san_pham,chi_tiet_don_hang,chi_tiet_phan_phoi
-- Techniques: IN subquery
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT ma_san_pham,ten_san_pham FROM san_pham WHERE ma_san_pham IN (SELECT ma_san_pham FROM chi_tiet_phan_phoi WHERE so_luong>30);


-- Query ID: M05_Q05
-- Title: Bao cao tong hop 5
-- Level: 2 - join
-- Tables: san_pham,chi_tiet_don_hang,chi_tiet_phan_phoi
-- Techniques: NOT EXISTS
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT p.ma_san_pham,p.ten_san_pham FROM san_pham p WHERE NOT EXISTS (SELECT 1 FROM chi_tiet_don_hang ct WHERE ct.ma_san_pham=p.ma_san_pham);


-- Query ID: M05_Q06
-- Title: Bao cao tong hop 6
-- Level: 2 - join
-- Tables: san_pham,chi_tiet_don_hang,chi_tiet_phan_phoi
-- Techniques: MAX
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT MAX(gia_ban) AS gia_max FROM san_pham;


-- Query ID: M05_Q07
-- Title: Bao cao tong hop 7
-- Level: 2 - join
-- Tables: san_pham,chi_tiet_don_hang,chi_tiet_phan_phoi
-- Techniques: MIN
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT MIN(gia_ban) AS gia_min FROM san_pham;


-- Query ID: M05_Q08
-- Title: Bao cao tong hop 8
-- Level: 3 - aggregate/subquery
-- Tables: san_pham,chi_tiet_don_hang,chi_tiet_phan_phoi
-- Techniques: SUM
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT SUM(so_luong) AS tong_ban FROM chi_tiet_don_hang;


-- Query ID: M05_Q09
-- Title: Bao cao tong hop 9
-- Level: 3 - aggregate/subquery
-- Tables: san_pham,chi_tiet_don_hang,chi_tiet_phan_phoi
-- Techniques: AVG
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT AVG(don_gia_ban) AS gia_ban_trung_binh FROM chi_tiet_don_hang;


-- Query ID: M05_Q10
-- Title: Bao cao tong hop 10
-- Level: 3 - aggregate/subquery
-- Tables: san_pham,chi_tiet_don_hang,chi_tiet_phan_phoi
-- Techniques: LEFT JOIN
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT p.ma_san_pham,p.ten_san_pham,COUNT(ct.ma_chi_tiet) AS so_dong FROM san_pham p LEFT JOIN chi_tiet_don_hang ct ON ct.ma_san_pham=p.ma_san_pham GROUP BY p.ma_san_pham,p.ten_san_pham;


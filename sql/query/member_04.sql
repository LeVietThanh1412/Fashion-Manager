-- Query ID: M04_Q01
-- Title: Don hang va doanh thu 1
-- Level: 1 - basic
-- Tables: don_hang,chi_tiet_don_hang,khach_hang
-- Techniques: JOIN, SUM, date function
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT DATE(d.ngay_tao_don) AS ngay, SUM(ct.so_luong*ct.don_gia_ban) AS doanh_thu FROM don_hang d JOIN chi_tiet_don_hang ct ON ct.ma_don_hang=d.ma_don_hang GROUP BY DATE(d.ngay_tao_don) ORDER BY ngay;


-- Query ID: M04_Q02
-- Title: Don hang va doanh thu 2
-- Level: 1 - basic
-- Tables: don_hang,chi_tiet_don_hang,khach_hang
-- Techniques: GROUP BY, COUNT
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT kh.ma_khach_hang,kh.ho_ten,COUNT(d.ma_don_hang) AS so_don FROM khach_hang kh LEFT JOIN don_hang d ON d.ma_khach_hang=kh.ma_khach_hang GROUP BY kh.ma_khach_hang,kh.ho_ten HAVING COUNT(d.ma_don_hang)>=1 ORDER BY so_don DESC;


-- Query ID: M04_Q03
-- Title: Don hang va doanh thu 3
-- Level: 1 - basic
-- Tables: don_hang,chi_tiet_don_hang,khach_hang
-- Techniques: JOIN, SUM, date function
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT DATE(d.ngay_tao_don) AS ngay, SUM(ct.so_luong*ct.don_gia_ban) AS doanh_thu FROM don_hang d JOIN chi_tiet_don_hang ct ON ct.ma_don_hang=d.ma_don_hang GROUP BY DATE(d.ngay_tao_don) ORDER BY ngay;


-- Query ID: M04_Q04
-- Title: Don hang va doanh thu 4
-- Level: 1 - basic
-- Tables: don_hang,chi_tiet_don_hang,khach_hang
-- Techniques: GROUP BY, COUNT
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT kh.ma_khach_hang,kh.ho_ten,COUNT(d.ma_don_hang) AS so_don FROM khach_hang kh LEFT JOIN don_hang d ON d.ma_khach_hang=kh.ma_khach_hang GROUP BY kh.ma_khach_hang,kh.ho_ten HAVING COUNT(d.ma_don_hang)>=1 ORDER BY so_don DESC;


-- Query ID: M04_Q05
-- Title: Don hang va doanh thu 5
-- Level: 2 - join
-- Tables: don_hang,chi_tiet_don_hang,khach_hang
-- Techniques: JOIN, SUM, date function
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT DATE(d.ngay_tao_don) AS ngay, SUM(ct.so_luong*ct.don_gia_ban) AS doanh_thu FROM don_hang d JOIN chi_tiet_don_hang ct ON ct.ma_don_hang=d.ma_don_hang GROUP BY DATE(d.ngay_tao_don) ORDER BY ngay;


-- Query ID: M04_Q06
-- Title: Don hang va doanh thu 6
-- Level: 2 - join
-- Tables: don_hang,chi_tiet_don_hang,khach_hang
-- Techniques: GROUP BY, COUNT
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT kh.ma_khach_hang,kh.ho_ten,COUNT(d.ma_don_hang) AS so_don FROM khach_hang kh LEFT JOIN don_hang d ON d.ma_khach_hang=kh.ma_khach_hang GROUP BY kh.ma_khach_hang,kh.ho_ten HAVING COUNT(d.ma_don_hang)>=1 ORDER BY so_don DESC;


-- Query ID: M04_Q07
-- Title: Don hang va doanh thu 7
-- Level: 2 - join
-- Tables: don_hang,chi_tiet_don_hang,khach_hang
-- Techniques: JOIN, SUM, date function
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT DATE(d.ngay_tao_don) AS ngay, SUM(ct.so_luong*ct.don_gia_ban) AS doanh_thu FROM don_hang d JOIN chi_tiet_don_hang ct ON ct.ma_don_hang=d.ma_don_hang GROUP BY DATE(d.ngay_tao_don) ORDER BY ngay;


-- Query ID: M04_Q08
-- Title: Don hang va doanh thu 8
-- Level: 3 - aggregate/subquery
-- Tables: don_hang,chi_tiet_don_hang,khach_hang
-- Techniques: GROUP BY, COUNT
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT kh.ma_khach_hang,kh.ho_ten,COUNT(d.ma_don_hang) AS so_don FROM khach_hang kh LEFT JOIN don_hang d ON d.ma_khach_hang=kh.ma_khach_hang GROUP BY kh.ma_khach_hang,kh.ho_ten HAVING COUNT(d.ma_don_hang)>=1 ORDER BY so_don DESC;


-- Query ID: M04_Q09
-- Title: Don hang va doanh thu 9
-- Level: 3 - aggregate/subquery
-- Tables: don_hang,chi_tiet_don_hang,khach_hang
-- Techniques: JOIN, SUM, date function
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT DATE(d.ngay_tao_don) AS ngay, SUM(ct.so_luong*ct.don_gia_ban) AS doanh_thu FROM don_hang d JOIN chi_tiet_don_hang ct ON ct.ma_don_hang=d.ma_don_hang GROUP BY DATE(d.ngay_tao_don) ORDER BY ngay;


-- Query ID: M04_Q10
-- Title: Don hang va doanh thu 10
-- Level: 3 - aggregate/subquery
-- Tables: don_hang,chi_tiet_don_hang,khach_hang
-- Techniques: GROUP BY, COUNT
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT kh.ma_khach_hang,kh.ho_ten,COUNT(d.ma_don_hang) AS so_don FROM khach_hang kh LEFT JOIN don_hang d ON d.ma_khach_hang=kh.ma_khach_hang GROUP BY kh.ma_khach_hang,kh.ho_ten HAVING COUNT(d.ma_don_hang)>=1 ORDER BY so_don DESC;


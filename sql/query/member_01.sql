-- Query ID: M01_Q01
-- Title: Danh sach san pham theo gia
-- Level: 1 - basic
-- Tables: san_pham
-- Techniques: WHERE, ORDER BY
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT ma_san_pham, ten_san_pham, gia_ban FROM san_pham WHERE gia_ban BETWEEN 150000 AND 400000 ORDER BY gia_ban, ma_san_pham;


-- Query ID: M01_Q02
-- Title: Tim san pham theo ten
-- Level: 1 - basic
-- Tables: san_pham
-- Techniques: LIKE
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT ma_san_pham, ten_san_pham, mau_sac FROM san_pham WHERE ten_san_pham LIKE '%5%' ORDER BY ten_san_pham;


-- Query ID: M01_Q03
-- Title: Danh muc theo alphabet
-- Level: 1 - basic
-- Tables: danh_muc
-- Techniques: ORDER BY, string function
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT ma_danh_muc, UPPER(ten_danh_muc) AS ten_in_hoa FROM danh_muc ORDER BY ten_danh_muc;


-- Query ID: M01_Q04
-- Title: San pham gia thap nhat
-- Level: 1 - basic
-- Tables: san_pham
-- Techniques: MIN
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT MIN(gia_ban) AS gia_thap_nhat, MAX(gia_ban) AS gia_cao_nhat FROM san_pham;


-- Query ID: M01_Q05
-- Title: San pham theo kich co
-- Level: 2 - join
-- Tables: san_pham
-- Techniques: WHERE
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT ma_san_pham, ten_san_pham, kich_co FROM san_pham WHERE kich_co IN ('M','L') ORDER BY ma_san_pham;


-- Query ID: M01_Q06
-- Title: San pham va danh muc
-- Level: 2 - join
-- Tables: san_pham,danh_muc
-- Techniques: JOIN
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT p.ma_san_pham, p.ten_san_pham, d.ten_danh_muc FROM san_pham p JOIN danh_muc d ON d.ma_danh_muc=p.ma_danh_muc ORDER BY d.ten_danh_muc,p.ma_san_pham;


-- Query ID: M01_Q07
-- Title: Dem san pham moi danh muc
-- Level: 2 - join
-- Tables: san_pham,danh_muc
-- Techniques: JOIN, GROUP BY, COUNT
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT d.ma_danh_muc,d.ten_danh_muc,COUNT(p.ma_san_pham) AS so_san_pham FROM danh_muc d LEFT JOIN san_pham p ON p.ma_danh_muc=d.ma_danh_muc GROUP BY d.ma_danh_muc,d.ten_danh_muc ORDER BY so_san_pham DESC;


-- Query ID: M01_Q08
-- Title: Gia trung binh danh muc
-- Level: 3 - aggregate/subquery
-- Tables: san_pham,danh_muc
-- Techniques: JOIN, AVG
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT d.ten_danh_muc,AVG(p.gia_ban) AS gia_trung_binh FROM danh_muc d JOIN san_pham p ON p.ma_danh_muc=d.ma_danh_muc GROUP BY d.ma_danh_muc,d.ten_danh_muc HAVING AVG(p.gia_ban)>200000;


-- Query ID: M01_Q09
-- Title: San pham cao hon gia trung binh
-- Level: 3 - aggregate/subquery
-- Tables: san_pham
-- Techniques: scalar subquery
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT ma_san_pham,ten_san_pham,gia_ban FROM san_pham WHERE gia_ban>(SELECT AVG(gia_ban) FROM san_pham) ORDER BY gia_ban DESC;


-- Query ID: M01_Q10
-- Title: Danh muc co san pham gia 0
-- Level: 3 - aggregate/subquery
-- Tables: danh_muc,san_pham
-- Techniques: EXISTS
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT d.ma_danh_muc,d.ten_danh_muc FROM danh_muc d WHERE EXISTS (SELECT 1 FROM san_pham p WHERE p.ma_danh_muc=d.ma_danh_muc AND p.gia_ban=0);


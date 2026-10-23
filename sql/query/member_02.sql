-- Query ID: M02_Q01
-- Title: Nhan vien va cua hang 1
-- Level: 1 - basic
-- Tables: nhan_vien,cua_hang
-- Techniques: JOIN
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT nv.ma_nhan_vien,nv.ho_ten,ch.ten_cua_hang FROM nhan_vien nv JOIN cua_hang ch ON ch.ma_cua_hang=nv.ma_cua_hang WHERE nv.ho_ten LIKE '%1%' ORDER BY nv.ma_nhan_vien;


-- Query ID: M02_Q02
-- Title: Nhan vien va cua hang 2
-- Level: 1 - basic
-- Tables: nhan_vien,cua_hang
-- Techniques: WHERE, string function
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT ma_nhan_vien,ho_ten,LOWER(email) AS email_thuong FROM nhan_vien WHERE ma_cua_hang='CH02' ORDER BY ho_ten;


-- Query ID: M02_Q03
-- Title: Nhan vien va cua hang 3
-- Level: 1 - basic
-- Tables: nhan_vien,cua_hang
-- Techniques: JOIN
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT nv.ma_nhan_vien,nv.ho_ten,ch.ten_cua_hang FROM nhan_vien nv JOIN cua_hang ch ON ch.ma_cua_hang=nv.ma_cua_hang WHERE nv.ho_ten LIKE '%3%' ORDER BY nv.ma_nhan_vien;


-- Query ID: M02_Q04
-- Title: Nhan vien va cua hang 4
-- Level: 1 - basic
-- Tables: nhan_vien,cua_hang
-- Techniques: WHERE, string function
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT ma_nhan_vien,ho_ten,LOWER(email) AS email_thuong FROM nhan_vien WHERE ma_cua_hang='CH04' ORDER BY ho_ten;


-- Query ID: M02_Q05
-- Title: Nhan vien va cua hang 5
-- Level: 2 - join
-- Tables: nhan_vien,cua_hang
-- Techniques: JOIN
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT nv.ma_nhan_vien,nv.ho_ten,ch.ten_cua_hang FROM nhan_vien nv JOIN cua_hang ch ON ch.ma_cua_hang=nv.ma_cua_hang WHERE nv.ho_ten LIKE '%5%' ORDER BY nv.ma_nhan_vien;


-- Query ID: M02_Q06
-- Title: Nhan vien va cua hang 6
-- Level: 2 - join
-- Tables: nhan_vien,cua_hang
-- Techniques: WHERE, string function
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT ma_nhan_vien,ho_ten,LOWER(email) AS email_thuong FROM nhan_vien WHERE ma_cua_hang='CH06' ORDER BY ho_ten;


-- Query ID: M02_Q07
-- Title: Nhan vien va cua hang 7
-- Level: 2 - join
-- Tables: nhan_vien,cua_hang
-- Techniques: JOIN
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT nv.ma_nhan_vien,nv.ho_ten,ch.ten_cua_hang FROM nhan_vien nv JOIN cua_hang ch ON ch.ma_cua_hang=nv.ma_cua_hang WHERE nv.ho_ten LIKE '%7%' ORDER BY nv.ma_nhan_vien;


-- Query ID: M02_Q08
-- Title: Nhan vien va cua hang 8
-- Level: 3 - aggregate/subquery
-- Tables: nhan_vien,cua_hang
-- Techniques: WHERE, string function
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT ma_nhan_vien,ho_ten,LOWER(email) AS email_thuong FROM nhan_vien WHERE ma_cua_hang='CH08' ORDER BY ho_ten;


-- Query ID: M02_Q09
-- Title: Nhan vien va cua hang 9
-- Level: 3 - aggregate/subquery
-- Tables: nhan_vien,cua_hang
-- Techniques: JOIN
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT nv.ma_nhan_vien,nv.ho_ten,ch.ten_cua_hang FROM nhan_vien nv JOIN cua_hang ch ON ch.ma_cua_hang=nv.ma_cua_hang WHERE nv.ho_ten LIKE '%9%' ORDER BY nv.ma_nhan_vien;


-- Query ID: M02_Q10
-- Title: Nhan vien va cua hang 10
-- Level: 3 - aggregate/subquery
-- Tables: nhan_vien,cua_hang
-- Techniques: WHERE, string function
-- Expected: Ket qua co y nghia voi seed deterministic
SELECT ma_nhan_vien,ho_ten,LOWER(email) AS email_thuong FROM nhan_vien WHERE ma_cua_hang='CH10' ORDER BY ho_ten;


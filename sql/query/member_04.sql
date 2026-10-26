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
-- Title: Don hang cua khach KH001
-- Level: 1 - basic
SELECT ma_don_hang,ma_nhan_vien,ngay_tao_don FROM don_hang WHERE ma_khach_hang='KH001' ORDER BY ngay_tao_don DESC;

-- Query ID: M04_Q04
-- Title: Don hang cung khach hang va nguoi lap
-- Level: 2 - join
SELECT d.ma_don_hang,d.ngay_tao_don,kh.ho_ten AS khach_hang,nv.ho_ten AS nguoi_lap FROM don_hang d JOIN khach_hang kh ON kh.ma_khach_hang=d.ma_khach_hang JOIN nhan_vien nv ON nv.ma_nhan_vien=d.ma_nhan_vien ORDER BY d.ma_don_hang;

-- Query ID: M04_Q05
-- Title: San pham va so luong trong don DH001
-- Level: 2 - join
SELECT ct.ma_don_hang,ct.ma_san_pham,sp.ten_san_pham,sp.mau_sac,sp.kich_co,ct.so_luong FROM chi_tiet_don_hang ct JOIN san_pham sp ON sp.ma_san_pham=ct.ma_san_pham WHERE ct.ma_don_hang='DH001' ORDER BY ct.ma_san_pham;

-- Query ID: M04_Q06
-- Title: Tong so luong ban theo san pham
-- Level: 3 - aggregate/subquery
SELECT sp.ma_san_pham,sp.ten_san_pham,SUM(ct.so_luong) AS tong_ban FROM san_pham sp JOIN chi_tiet_don_hang ct ON ct.ma_san_pham=sp.ma_san_pham GROUP BY sp.ma_san_pham,sp.ten_san_pham ORDER BY tong_ban DESC;

-- Query ID: M04_Q07
-- Title: Gia tri ban theo thang voi gia san pham hien hanh
-- Level: 3 - aggregate/subquery
SELECT DATE_FORMAT(d.ngay_tao_don,'%Y-%m') AS thang,SUM(ct.so_luong*sp.gia_san_pham) AS gia_tri_theo_gia_hien_hanh FROM don_hang d JOIN chi_tiet_don_hang ct ON ct.ma_don_hang=d.ma_don_hang JOIN san_pham sp ON sp.ma_san_pham=ct.ma_san_pham GROUP BY DATE_FORMAT(d.ngay_tao_don,'%Y-%m') ORDER BY thang;

-- Query ID: M04_Q08
-- Title: So don lap boi tung nhan vien
-- Level: 3 - aggregate/subquery
SELECT nv.ma_nhan_vien,nv.ho_ten,COUNT(d.ma_don_hang) AS so_don FROM nhan_vien nv LEFT JOIN don_hang d ON d.ma_nhan_vien=nv.ma_nhan_vien GROUP BY nv.ma_nhan_vien,nv.ho_ten ORDER BY so_don DESC;

-- Query ID: M04_Q09
-- Title: So don hang tai tung cua hang
-- Level: 3 - aggregate/subquery
SELECT ch.ma_cua_hang,ch.ten_cua_hang,COUNT(d.ma_don_hang) AS so_don FROM cua_hang ch LEFT JOIN nhan_vien nv ON nv.ma_cua_hang=ch.ma_cua_hang LEFT JOIN don_hang d ON d.ma_nhan_vien=nv.ma_nhan_vien GROUP BY ch.ma_cua_hang,ch.ten_cua_hang ORDER BY so_don DESC;

-- Query ID: M04_Q10
-- Title: Khach hang chua co don hang
-- Level: 3 - aggregate/subquery
SELECT kh.ma_khach_hang,kh.ho_ten FROM khach_hang kh WHERE NOT EXISTS (SELECT 1 FROM don_hang d WHERE d.ma_khach_hang=kh.ma_khach_hang) ORDER BY kh.ma_khach_hang;


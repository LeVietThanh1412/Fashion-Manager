-- 1. Hiển thị toàn bộ danh sách sản phẩm.
SELECT *
FROM v_san_pham;

-- 2. Hiển thị mã, họ tên và lương của nhân viên tại CH001.
SELECT ma_nhan_vien, ho_ten, luong
FROM v_nhan_vien
WHERE ma_cua_hang = 'CH001';
-- 3. Tìm đơn hàng được tạo trong tháng 3 năm 2026.
SELECT *
FROM v_don_hang
WHERE MONTH(ngay_tao_don) = 3
  AND YEAR(ngay_tao_don) = 2026;
-- 4. Tìm sản phẩm có tên chứa từ "Giày".
SELECT *
FROM v_san_pham
WHERE ten_san_pham LIKE '%Giày%';
-- 5. Tìm sản phẩm có giá lớn hơn 540.000 đồng.
SELECT ma_san_pham, ten_san_pham, gia_san_pham
FROM v_san_pham
WHERE gia_san_pham > 540000;
-- 6. Hiển thị chi tiết đơn DH003.
-- Thành tiền dùng đơn giá và giảm giá lịch sử đã lưu trên đơn.
SELECT A.ma_don_hang, B.ma_san_pham, B.ten_san_pham,
       A.so_luong, A.don_gia_ban, A.giam_gia,
       (A.so_luong * A.don_gia_ban - A.giam_gia)
FROM v_chi_tiet_don_hang A, v_san_pham B
WHERE A.ma_san_pham = B.ma_san_pham
  AND A.ma_don_hang = 'DH003';
-- 7. Hiển thị các khách hàng từng mua sản phẩm SP001.
SELECT DISTINCT A.ma_khach_hang, A.ho_ten, A.so_dien_thoai
FROM khach_hang A, v_don_hang B, v_chi_tiet_don_hang C
WHERE A.ma_khach_hang = B.ma_khach_hang
  AND B.ma_don_hang = C.ma_don_hang
  AND C.ma_san_pham = 'SP001';
-- 8. Hiển thị các khách hàng từng mua tại cửa hàng CH002.
SELECT DISTINCT A.ma_khach_hang, A.ho_ten
FROM khach_hang A, v_don_hang B, v_nhan_vien C
WHERE A.ma_khach_hang = B.ma_khach_hang
  AND B.ma_nhan_vien = C.ma_nhan_vien
  AND B.ma_cua_hang = 'CH002';
-- 9. Hiển thị sản phẩm đã bán trong tháng 6 năm 2026.
SELECT DISTINCT A.ma_san_pham, A.ten_san_pham
FROM v_san_pham A, v_chi_tiet_don_hang B, v_don_hang C
WHERE A.ma_san_pham = B.ma_san_pham
  AND B.ma_don_hang = C.ma_don_hang
  AND MONTH(C.ngay_tao_don) = 6
  AND YEAR(C.ngay_tao_don) = 2026;
-- 10. Sắp xếp nhân viên theo lương giảm dần,
-- nếu bằng lương thì mã nhân viên tăng dần.
SELECT ma_nhan_vien, ho_ten, luong
FROM v_nhan_vien
ORDER BY luong DESC, ma_nhan_vien ASC;
-- 11. Hiển thị sản phẩm có tổng số lượng đã bán trên 20.
SELECT A.ma_san_pham, A.ten_san_pham, SUM(B.so_luong) as tong_so_luong
FROM v_san_pham A, v_chi_tiet_don_hang B
WHERE A.ma_san_pham = B.ma_san_pham
GROUP BY A.ma_san_pham, A.ten_san_pham
HAVING SUM(B.so_luong) > 20;
-- 12. Thống kê số đơn hàng của từng nhân viên đã bán hàng.
SELECT A.ma_nhan_vien, A.ho_ten, COUNT(B.ma_don_hang) AS so_don_hang
FROM v_nhan_vien A, v_don_hang B
WHERE A.ma_nhan_vien = B.ma_nhan_vien
GROUP BY A.ma_nhan_vien, A.ho_ten;
-- 13. Tìm nhân viên có lương cao hơn lương trung bình.
SELECT ma_nhan_vien, ho_ten, luong
FROM v_nhan_vien
WHERE luong > (
    SELECT AVG(luong)
    FROM v_nhan_vien
);
-- 14. Giá thấp nhất, cao nhất và trung bình theo danh mục.
SELECT A.ma_danh_muc, A.ten_danh_muc,
       (SELECT MIN(B.gia_san_pham)
        FROM v_san_pham B
        WHERE B.ma_danh_muc = A.ma_danh_muc) AS gia_thap_nhat,

       (SELECT MAX(B.gia_san_pham)
        FROM v_san_pham B
        WHERE B.ma_danh_muc = A.ma_danh_muc) AS gia_cao_nhat,

       (SELECT AVG(B.gia_san_pham)
        FROM v_san_pham B
        WHERE B.ma_danh_muc = A.ma_danh_muc) AS gia_trung_binh

FROM danh_muc A;
-- 15. Tìm sản phẩm mà cả KH003 và KH002 đều từng mua.
SELECT A.ma_san_pham, A.ten_san_pham
FROM v_san_pham A
WHERE A.ma_san_pham IN (
    SELECT B.ma_san_pham
    FROM v_chi_tiet_don_hang B, v_don_hang C
    WHERE B.ma_don_hang = C.ma_don_hang
      AND C.ma_khach_hang = 'KH003'
)
AND A.ma_san_pham IN (
    SELECT D.ma_san_pham
    FROM v_chi_tiet_don_hang D, v_don_hang E
    WHERE D.ma_don_hang = E.ma_don_hang
      AND E.ma_khach_hang = 'KH002'
);

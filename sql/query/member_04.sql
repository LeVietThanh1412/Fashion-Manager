-- 1. Danh sách các sản phẩm có giá từ 1.000.000 VNĐ trở lên, sắp xếp theo giảm dần
SELECT * FROM v_san_pham
WHERE gia_san_pham >= 1000000
ORDER BY gia_san_pham DESC;

-- 2. Hiển thị danh sách khách hàng có họ "Vũ"
SELECT * FROM khach_hang
WHERE ho_ten LIKE N'Vũ%';

-- 3. Liệt kê danh sách các cửa hàng thuộc miền Bắc (Khu vực 1)
SELECT ma_cua_hang, ten_cua_hang, dia_chi, so_dien_thoai, email
FROM cua_hang
WHERE khu_vuc = 1;

-- 4. Tìm sản phẩm thuộc danh mục "Giày sneaker" (DM001) có kích cỡ 38, 39
SELECT * FROM v_san_pham
WHERE ma_danh_muc = 'DM001' AND kich_co IN ('38', '39');

-- 5. Hiển thị danh sách sản phẩm cùng tên danh mục tương ứng
SELECT sp.*, d.ten_danh_muc FROM v_san_pham sp, danh_muc d
WHERE sp.ma_danh_muc = d.ma_danh_muc;

-- 6. Liệt kê thông tin chi tiết đơn hàng (tên khách hàng, tên nhân viên bán, ngày tạo đơn)
SELECT dh.ma_don_hang, kh.ho_ten AS ten_khach_hang, nv.ho_ten AS ten_nhan_vien, dh.ngay_tao_don
FROM v_don_hang dh, khach_hang kh, v_nhan_vien nv
WHERE dh.ma_khach_hang = kh.ma_khach_hang
AND dh.ma_nhan_vien = nv.ma_nhan_vien;

-- 7. Hiển thị danh sách nhân viên cùng tên cửa hàng nơi họ làm việc và tên người quản lý trực tiếp
SELECT nv.ma_nhan_vien, nv.ho_ten AS ten_nhan_vien, ch.ten_cua_hang, ql.ho_ten AS ten_nguoi_quan_ly
FROM v_nhan_vien nv, cua_hang ch, v_nhan_vien ql
WHERE nv.ma_cua_hang = ch.ma_cua_hang
AND nv.ma_quan_ly = ql.ma_nhan_vien;

-- 8. Hiển thị chi tiết các sản phẩm trong đơn hàng 'DH010'(tên sp, size, số lượng, đơn giá, thành tiền)
SELECT ctdh.ma_don_hang, sp.ten_san_pham, sp.kich_co, ctdh.so_luong, ctdh.don_gia_ban, ctdh.giam_gia,
       ((ctdh.so_luong * ctdh.don_gia_ban - ctdh.giam_gia)) AS thanh_tien
FROM v_chi_tiet_don_hang ctdh, v_san_pham sp
WHERE ctdh.ma_san_pham = sp.ma_san_pham
AND ctdh.ma_don_hang = 'DH010';

-- 9. Tìm tên khách hàng đã từng mua sản phẩm "Sneaker Urban Low"
SELECT DISTINCT kh.ma_khach_hang, kh.ho_ten, kh.so_dien_thoai
FROM khach_hang kh, v_don_hang dh, v_chi_tiet_don_hang ctdh, v_san_pham sp
WHERE kh.ma_khach_hang = dh.ma_khach_hang
AND dh.ma_don_hang = ctdh.ma_don_hang
AND ctdh.ma_san_pham = sp.ma_san_pham
AND sp.ten_san_pham = N'Sneaker Urban Low';

-- 10. Thống kê tổng số lượng bán ra của từng dòng sản phẩm
SELECT sp.ten_san_pham, SUM(ctdh.so_luong) AS tong_so_luong_ban,
COUNT(DISTINCT ctdh.ma_don_hang) AS so_lan_xuat_hien
FROM v_san_pham sp, v_chi_tiet_don_hang ctdh
WHERE sp.ma_san_pham = ctdh.ma_san_pham
GROUP BY sp.ten_san_pham
ORDER BY tong_so_luong_ban DESC;

-- 11. Thống kê tổng giá trị của từng đơn hàng và lọc ra các đơn hàng có tổng tiền trên 3.000.000 VNĐ
SELECT dh.ma_don_hang, dh.ngay_tao_don,
SUM((ctdh.so_luong * ctdh.don_gia_ban - ctdh.giam_gia)) AS tong_gia_tri_don
FROM v_don_hang dh, v_chi_tiet_don_hang ctdh, v_san_pham sp
WHERE dh.ma_don_hang = ctdh.ma_don_hang
AND ctdh.ma_san_pham = sp.ma_san_pham
GROUP BY dh.ma_don_hang, dh.ngay_tao_don
HAVING SUM((ctdh.so_luong * ctdh.don_gia_ban - ctdh.giam_gia)) > 3000000;

-- 12. Lương trung bình, cao nhất, thấp nhất của từng cửa hàng
SELECT ch.ten_cua_hang,
AVG(nv.luong) AS luong_trung_binh,
MAX(nv.luong) AS luong_cao_nhat,
MIN(nv.luong) AS luong_thap_nhat
FROM v_nhan_vien nv, cua_hang ch
WHERE nv.ma_cua_hang = ch.ma_cua_hang
GROUP BY ch.ten_cua_hang;

-- 13. Tìm các mã sản phẩm chưa từng bán được trong bất kì đơn hàng nào
SELECT ma_san_pham, ten_san_pham, mau_sac, kich_co, gia_san_pham
FROM v_san_pham
WHERE ma_san_pham NOT IN (SELECT DISTINCT ma_san_pham
FROM v_chi_tiet_don_hang);

-- 14. Tìm khách hàng mua nhiều đơn hàng nhất hệ thống
SELECT kh.ma_khach_hang, kh.ho_ten, COUNT(dh.ma_don_hang) AS tong_so_don_hang
FROM khach_hang kh, v_don_hang dh
WHERE kh.ma_khach_hang = dh.ma_khach_hang
GROUP BY kh.ma_khach_hang, kh.ho_ten
HAVING COUNT(dh.ma_don_hang) >= ALL (SELECT COUNT(ma_don_hang)
FROM v_don_hang
GROUP BY ma_khach_hang);

-- 15. Tổng hợp danh sách SĐT và tên của khách hàng và nhân viên
SELECT ho_ten, so_dien_thoai, N'Khách hàng' AS loai_doi_tuong
FROM khach_hang
UNION
SELECT ho_ten, so_dien_thoai, N'Nhân viên' AS loai_doi_tuong
FROM v_nhan_vien;

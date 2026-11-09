-- 1. Hiển thị toàn bộ danh sách sản phẩm.
SELECT * FROM v_san_pham;
-- 2. Hiển thị các sản phẩm thuộc danh mục có mã 'DM001'.
SELECT * FROM v_san_pham
WHERE ma_danh_muc = 'DM001';
-- 3. Tìm các sản phẩm có giá sản phẩm lớn hơn 200,000 VNĐ.
SELECT * FROM v_san_pham
WHERE gia_san_pham > 200000;
-- 4. Sắp xếp danh sách nhân viên theo mức lương giảm dần.
SELECT ma_nhan_vien, ho_ten, luong, ma_cua_hang
FROM v_nhan_vien
ORDER BY luong DESC;
-- ORDER BY luong DESC dùng để sắp xếp kết quả dựa trên cột luong theo thứ tự giảm dần
-- 5. Tìm kiếm các khách hàng có họ tên bắt đầu bằng chữ 'Nguyễn'.
SELECT * FROM khach_hang
WHERE ho_ten LIKE 'Nguyễn%';
-- Ký tự % là ký tự đại diện cho bất kỳ chuỗi ký tự ở sau (kể cả rỗng), giúp lọc các tên bắt đầu bằng chữ "Nguyễn".
-- b. Truy vấn nhiều bảng
-- 6. Hiển thị danh sách sản phẩm kèm theo tên danh mục tương ứng.
SELECT sp.ma_san_pham, sp.ten_san_pham, dm.ten_danh_muc, sp.gia_san_pham
FROM v_san_pham sp, danh_muc dm
WHERE sp.ma_danh_muc = dm.ma_danh_muc;

-- 7. Liệt kê thông tin các đơn hàng gồm: mã đơn hàng, ngày tạo đơn, họ tên khách hàng và họ tên nhân viên lập đơn.
SELECT dh.ma_don_hang, dh.ngay_tao_don, kh.ho_ten AS ten_khach_hang, nv.ho_ten AS ten_nhan_vien
FROM v_don_hang dh, khach_hang kh, v_nhan_vien nv
WHERE dh.ma_khach_hang = kh.ma_khach_hang AND dh.ma_nhan_vien = nv.ma_nhan_vien;
-- 8. Xem chi tiết các dòng sản phẩm có trong một đơn hàng cụ thể (ví dụ: mã đơn hàng 'DH001')
SELECT ct.ma_don_hang,ct.ma_san_pham,sp.ten_san_pham,ct.so_luong,ct.don_gia_ban,ct.giam_gia,
ct.so_luong*ct.don_gia_ban-ct.giam_gia AS thanh_tien
FROM v_chi_tiet_don_hang ct JOIN v_san_pham sp ON sp.ma_san_pham=ct.ma_san_pham
WHERE ct.ma_don_hang='DH001';

 -- 9. Tìm tất cả các đơn hàng được tạo bởi các nhân viên đang làm việc tại cửa hàng có mã 'CH001', sắp xếp theo ngày tạo đơn tăng dần
SELECT dh.ma_don_hang,dh.ngay_tao_don,nv.ma_nhan_vien,nv.ho_ten,dh.ma_cua_hang
FROM v_don_hang dh JOIN nhan_vien nv ON nv.ma_nhan_vien=dh.ma_nhan_vien
WHERE dh.ma_cua_hang='CH001' ORDER BY dh.ngay_tao_don;

-- 10. Hiển thị thông tin chi tiết các sản phẩm có mặt trong các phiếu phân phối (Mã phiếu, ngày phân phối, tên sản phẩm, số lượng phân phối)
SELECT pp.ma_phan_phoi, pp.ngay_phan_phoi, sp.ten_san_pham, ctpp.so_luong
FROM v_chi_tiet_phan_phoi ctpp, v_phan_phoi pp, v_san_pham sp
WHERE ctpp.ma_phan_phoi = pp.ma_phan_phoi
 AND ctpp.ma_san_pham = sp.ma_san_pham;
-- c. Gom nhóm, thống kê và truy vấn lồng nhau
-- 11. Tính tổng giá trị của từng đơn hàng và chỉ hiển thị các đơn hàng có tổng tiền lớn hơn 1.000.000 VNĐ (GROUP BY và HAVING)
SELECT ctdh.ma_don_hang, SUM((ctdh.so_luong * ctdh.don_gia_ban - ctdh.giam_gia)) as tong_tien_don_hang
FROM v_chi_tiet_don_hang ctdh, v_san_pham sp
WHERE ctdh.ma_san_pham = sp.ma_san_pham
GROUP BY ctdh.ma_don_hang
HAVING SUM((ctdh.so_luong * ctdh.don_gia_ban - ctdh.giam_gia)) > 1000000;
-- 12. Tìm mức lương cao nhất, thấp nhất và mức lương trung bình của toàn bộ nhân viên trong hệ thống
SELECT MAX(luong) luong_cao_nhat,
       MIN(luong) luong_thap_nhat,
       AVG(luong) luong_trung_binh
FROM v_nhan_vien;
-- 13. Tìm các sản phẩm có giá bán cao hơn mức giá bán trung bình của tất cả các sản phẩm (Truy vấn lồng nhau)
SELECT ma_san_pham, ten_san_pham, mau_sac, kich_co, gia_san_pham
FROM v_san_pham
WHERE gia_san_pham > (SELECT AVG(gia_san_pham) FROM v_san_pham);
-- 14. Liệt kê thông tin những khách hàng đã từng phát sinh ít nhất một đơn hàng trong hệ thống
SELECT ma_khach_hang, ho_ten, so_dien_thoai
FROM khach_hang
WHERE ma_khach_hang IN (
    SELECT DISTINCT ma_khach_hang
    FROM v_don_hang);
-- 15. Lấy danh sách gồm mã định danh, họ tên và số điện thoại của cả Khách hàng và Nhân viên bằng cách sử dụng phép tập hợp UNION
SELECT ma_khach_hang ma_dinh_danh, ho_ten, so_dien_thoai, 'Khách hàng' vai_tro
FROM khach_hang
UNION
SELECT ma_nhan_vien ma_dinh_danh, ho_ten, so_dien_thoai, 'Nhân viên' vai_tro
FROM v_nhan_vien;
-- 16. Tìm mã của những khách hàng ĐÃ TỪNG mua cả sản phẩm 'SP001' VÀ sản phẩm 'SP002'
SELECT dh.ma_khach_hang FROM v_don_hang dh JOIN v_chi_tiet_don_hang ct ON ct.ma_don_hang=dh.ma_don_hang WHERE ct.ma_san_pham='SP001'
INTERSECT
SELECT dh.ma_khach_hang FROM v_don_hang dh JOIN v_chi_tiet_don_hang ct ON ct.ma_don_hang=dh.ma_don_hang WHERE ct.ma_san_pham='SP002';

-- 17. Khách hàng chưa từng phát sinh đơn hàng
SELECT ma_khach_hang FROM khach_hang
EXCEPT
SELECT ma_khach_hang FROM v_don_hang;

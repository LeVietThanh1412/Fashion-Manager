-- 1.  Đưa ra danh sách chi nhánh của hàng nằm tại Hà nội
select *from cua_hang where dia_chi like'%Ha Noi%' ;
-- 2. Đưa ra danh sách cửa hàng nằm trong khu vực 1 và khu vực 2
select ma_cua_hang, ten_cua_hang, dia_chi, so_dien_thoai, email, khu_vuc
from cua_hang
where khu_vuc in (1,2);
-- 3. Liệt kê danh sách tất cả các nhân viên (gồm mã nhân viên, họ tên, lương) có mức lương lớn hơn 10 triệu đồng
select ma_nhan_vien, ho_ten, luong
from v_nhan_vien
where luong > 10000000;
-- 4. Lương trung bình của toàn bộ nhân viên
select avg(luong) as luong_trung_binh from v_nhan_vien ;
-- 5. Lương trung bình của những người giữ chức vụ là nhân viên bình thường
select avg(luong) as luong_trung_binh_nhan_vien
from v_nhan_vien
where exists (select 1 from tai_khoan tk join phan_cong_quyen pc on pc.ma_tai_khoan=tk.ma_tai_khoan where tk.ma_nhan_vien=v_nhan_vien.ma_nhan_vien and pc.ma_vai_tro='sales_staff' and pc.trang_thai='active' and pc.thu_hoi_luc is null and pc.tu_ngay<=UTC_TIMESTAMP() and (pc.den_ngay is null or UTC_TIMESTAMP()<pc.den_ngay));
-- 6. Danh sách nhân viên có lương cao hơn mức lương trung bình nhân viên
select ma_nhan_vien, ho_ten, luong, ma_cua_hang
from v_nhan_vien
where luong > (
    select avg(luong)
    from v_nhan_vien
);
-- 7. Những phiếu phân phối do nhân viên NV004 phụ trách
select *  from v_phan_phoi where ma_nhan_vien = 'NV004';
-- 8. Danh sách các đơn hàng (gồm mã đơn hàng, ngày tạo đơn), thông tin khách hàng đặt đơn (tên khách hàng, số điện thoại) và tên nhân viên phụ trách bán hàng của những đơn hàng được tạo trong tháng 5/2026.
select
    dh.ma_don_hang,
    dh.ngay_tao_don,
    kh.ho_ten as ten_khach_hang,
    kh.so_dien_thoai,
    nv.ho_ten as ten_nhan_vien_ban_hang
from v_don_hang dh
join khach_hang kh on dh.ma_khach_hang = kh.ma_khach_hang
join v_nhan_vien nv on dh.ma_nhan_vien = nv.ma_nhan_vien
where dh.ngay_tao_don >= '2026-05-01 00:00:00'
	and dh.ngay_tao_don < '2026-06-01 00:00:00';
-- 9. Cho biết thông tin những nhân viên phụ trách đơn hàng trong tháng 5/2026
select dh.ma_don_hang, nv.* from v_nhan_vien nv
join v_don_hang dh on nv.ma_nhan_vien=dh.ma_nhan_vien
	where ngay_tao_don >= '2026-05-01 '
	and ngay_tao_don < '2026-06-01 ' ;
-- 10. Nhân viên phụ trách nhiều đơn hàng nhất
  select
    nv.ma_nhan_vien,
    nv.ho_ten,
    count(dh.ma_don_hang) as tong_so_don_hang
from v_nhan_vien nv
join v_don_hang dh on nv.ma_nhan_vien = dh.ma_nhan_vien
group by nv.ma_nhan_vien, nv.ho_ten
order by tong_so_don_hang desc
limit 1;
-- 11. Sản phẩm có lượt bán ra cao nhất ( gồm tất cả các phiên bản )
select
    sp.ten_san_pham,
    sum(ctdh.so_luong) as tong_so_luong_da_ban
from v_san_pham sp
join v_chi_tiet_don_hang ctdh on sp.ma_san_pham = ctdh.ma_san_pham
group by sp.ten_san_pham
order by tong_so_luong_da_ban desc
limit 1;

-- 12. Các sản phẩm chưa từng được phân phối lần nào vào bất kỳ cửa hàng nào
select distinct ten_san_pham
from v_san_pham
where ten_san_pham not in (
    select distinct sp.ten_san_pham
    from v_san_pham sp
    join v_chi_tiet_phan_phoi ctpp on sp.ma_san_pham = ctpp.ma_san_pham
);
-- 13. Tổng số lượng của sản phẩm mang mã SP002 được phân phối đến các của hàng
select sp.ma_san_pham , sp.ten_san_pham , sum(ct.so_luong) as tong_so_luong_phan_phoi
from v_chi_tiet_phan_phoi ct
join v_san_pham sp on ct.ma_san_pham = sp.ma_san_pham
where sp.ma_san_pham = 'SP002'
group by sp.ma_san_pham, sp.ten_san_pham ;

-- 14. Tổng số sản phẩm mang mã SP002 đã được bán
select
    sp.ma_san_pham,
    sp.ten_san_pham,
    sum(ctdh.so_luong) as tong_da_ban
from v_chi_tiet_don_hang ctdh
join v_san_pham sp on ctdh.ma_san_pham = sp.ma_san_pham
where sp.ma_san_pham = 'SP002'
group by sp.ma_san_pham, sp.ten_san_pham;

-- 15. Tổng số sản phẩm mang mã SP002 còn lại trong các cửa hàng
SELECT t.ma_san_pham,sp.ten_san_pham,SUM(t.so_luong) AS so_luong_con_lai
FROM ton_kho t JOIN kho k ON k.ma_kho=t.ma_kho
JOIN v_san_pham sp ON sp.ma_san_pham=t.ma_san_pham
WHERE t.ma_san_pham='SP002' AND k.loai_kho='store'
GROUP BY t.ma_san_pham,sp.ten_san_pham;


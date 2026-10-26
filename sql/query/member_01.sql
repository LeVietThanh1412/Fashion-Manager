-- MỨC 1 - TRUY VẤN CƠ BẢN
-- 1. In ra tất cả các sản phẩm áo có giá từ 100.000 - 300.000
select *
from san_pham
where ten_san_pham like 'Áo %' and gia_san_pham between 100000 and 300000
order by ma_san_pham;

-- 2. In ra các nhân viên có lương trên 6500000
select * 
from nhan_vien
where luong > 6500000
order by ma_nhan_vien;

-- 3. In ra các nhân viên thuộc cửa hàng 001
select * 
from nhan_vien
where ma_cua_hang = 'CH001';

-- 4. Hiển thị danh sách sản phẩm theo giá tăng dần hoặc giảm dần.
select *
from san_pham
order by gia_san_pham desc;

-- MỨC 2 - TRUY VẤN NHIỀU BẢNG
-- 5. Hiển thị nhân viên cùng tên cửa hàng và khu vực cửa hàng đang làm việc.
select nv.ho_ten as 'Họ và tên', ch.ten_cua_hang as 'Cửa hàng', CasE 
    when ch.khu_vuc = 1 then 'Miền Bắc'
    when ch.khu_vuc = 2 then 'Miền Trung'
    ELSE  'Miền Nam'
END as 'Khu vực'

from nhan_vien as nv
join cua_hang as ch on ch.ma_cua_hang = nv.ma_cua_hang;

-- 6. Hiển thị đơn hàng cùng tên khách hàng và nhân viên tạo đơn.
select dh.ma_don_hang as 'Đơn hàng', kh.ho_ten as 'Khách hàng', nv.ho_ten as 'Nhân viên tạo đơn'
from don_hang as dh
join khach_hang as kh on dh.ma_khach_hang = kh.ma_khach_hang
join nhan_vien as nv on dh.ma_nhan_vien = nv.ma_nhan_vien;

-- 7. Hiển thị các sản phẩm trong từng phiếu phân phối, kèm tên cửa hàng và số lượng phân phối.
select pp.ma_phan_phoi as 'Phiếu phân phối', ch.ten_cua_hang as 'Cửa hàng', sp.ten_san_pham as 'Sản phẩm', ctpp.so_luong as 'Số lượng'
from chi_tiet_phan_phoi as ctpp
join san_pham as sp on ctpp.ma_san_pham = sp.ma_san_pham
join phan_phoi as pp on ctpp.ma_phan_phoi = pp.ma_phan_phoi
join nhan_vien as nv on pp.ma_nhan_vien = nv.ma_nhan_vien
join cua_hang as ch on nv.ma_nhan_vien = ch.ma_cua_hang

-- MỨC 3 - GOM NHÓM, THỐNG KÊ VÀ TRUY VẤN LỒNG NHAU
-- 8. Thống kê số nhân viên của từng cửa hàng; chỉ hiển thị cửa hàng có số nhân viên từ 3 trở lên.
select  ch.ten_cua_hang as 'Tên cửa hàng', count(nv.ma_nhan_vien) as 'Số lượng nhân viên'
from nhan_vien as nv
join cua_hang as ch on nv.ma_cua_hang = ch.ma_cua_hang
where nv.ma_cua_hang is not null
group by nv.ma_cua_hang
having count(nv.ma_nhan_vien) > 3
order by nv.ma_cua_hang;


-- 9. Tính tổng số lượng phân phối theo từng cửa hàng và sản phẩm.
select ch.ten_cua_hang as 'Cửa hàng', sp.ten_san_pham as 'Sản phẩm', sum(ctpp.so_luong) as 'Số lượng'
from chi_tiet_phan_phoi as ctpp
join phan_phoi as pp on ctpp.ma_phan_phoi = pp.ma_phan_phoi
join nhan_vien as nv on nv.ma_nhan_vien = pp.ma_nhan_vien
join cua_hang as ch on ch.ma_cua_hang = nv.ma_cua_hang
join san_pham as sp on sp.ma_san_pham = ctpp.ma_san_pham
group by ch.ma_cua_hang,  sp.ma_san_pham
order by ch.ten_cua_hang, sp.ten_san_pham;

-- 11. Tìm cửa hàng có tổng doanh thu lớn hơn mức doanh thu trung bình của các cửa hàng.
with doanh_thu_cua_hang as (
    select ch.ma_cua_hang, sum(ctdh.so_luong * sp.gia_san_pham) as tong_doanh_thu
    from chi_tiet_don_hang as ctdh
    join san_pham as sp on ctdh.ma_san_pham = sp.ma_san_pham
    join don_hang as dh on ctdh.ma_don_hang = dh.ma_don_hang
    join nhan_vien as nv on dh.ma_nhan_vien = nv.ma_nhan_vien
    join cua_hang as ch on nv.ma_cua_hang = ch.ma_cua_hang
    group by ch.ma_cua_hang
)
select ch.ten_cua_hang, dtch.tong_doanh_thu
from cua_hang as ch
join doanh_thu_cua_hang as dtch on ch.ma_cua_hang = dtch.ma_cua_hang
where dtch.tong_doanh_thu > (select avg(doanh_thu_cua_hang.tong_doanh_thu) from doanh_thu_cua_hang)
order by dtch.tong_doanh_thu desc;

-- 12. In ra các nhân viên có tổng doanh thu cao nhất của từng cửa hàng 
with doanh_thu as (
    select ch.ma_cua_hang, ch.ten_cua_hang, nv.ma_nhan_vien, nv.ho_ten, sum(ctdh.so_luong * sp.gia_san_pham) as doanh_thu_nv
    from nhan_vien as nv
    join cua_hang as ch on nv.ma_cua_hang = ch.ma_cua_hang
    join don_hang as dh on nv.ma_nhan_vien = dh.ma_nhan_vien
    join chi_tiet_don_hang as ctdh on dh.ma_don_hang = ctdh.ma_don_hang
    join san_pham as sp on ctdh.ma_san_pham = sp.ma_san_pham
    group by ch.ma_cua_hang, nv.ma_nhan_vien
)
select dt.ten_cua_hang as 'Cửa hàng', dt.ho_ten as 'Họ tên', dt.doanh_thu_nv as 'Doanh thu'
from doanh_thu as dt
where dt.doanh_thu_nv = (
    select max(dt2.doanh_thu_nv)
    from doanh_thu as dt2
    where dt2.ma_cua_hang = dt.ma_cua_hang
)
order by dt.ma_cua_hang;

-- xếp hạng doanh thu các cửa hàng khu vực miền Bắc


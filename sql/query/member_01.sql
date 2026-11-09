-- MỨC 1 - TRUY VẤN CƠ BẢN
-- 1. In ra tất cả các sản phẩm Dép có giá từ 100.000 - 300.000
select *
from v_san_pham
where ten_san_pham like 'Dép %'
    and gia_san_pham between 100000 and 300000
order by ma_san_pham;

-- 2. In ra các nhân viên có lương trên 6500000
select *
from v_nhan_vien
where luong > 6500000
order by ma_nhan_vien;

-- 3. In ra các nhân viên thuộc cửa hàng 001
select *
from v_nhan_vien
where ma_cua_hang = 'CH001';

-- 4. Hiển thị danh sách sản phẩm theo giá tăng giảm dần.
select *
from v_san_pham
order by gia_san_pham desc;

-- MỨC 2 - TRUY VẤN NHIỀU BẢNG
-- 5. Hiển thị nhân viên, tên cửa hàng và khu vực cửa hàng đang làm việc.
SELECT nv.ho_ten,ch.ten_cua_hang,kv.ten_khu_vuc
FROM v_nhan_vien nv JOIN cua_hang ch ON ch.ma_cua_hang=nv.ma_cua_hang
JOIN khu_vuc kv ON kv.ma_khu_vuc=ch.khu_vuc;


-- 6. Hiển thị đơn hàng cùng tên khách hàng và nhân viên tạo đơn.
select dh.ma_don_hang as 'Đơn hàng',
       kh.ho_ten as 'Khách hàng',
       nv.ho_ten as 'Nhân viên tạo đơn'
from v_don_hang as dh
join khach_hang as kh on dh.ma_khach_hang = kh.ma_khach_hang
join v_nhan_vien as nv on dh.ma_nhan_vien = nv.ma_nhan_vien;

-- 7. In ra quản lý của từng cửa hàng
SELECT pc.ma_cua_hang,nv.ho_ten,pc.tu_ngay,pc.den_ngay
FROM phan_cong_quyen pc JOIN tai_khoan tk ON tk.ma_tai_khoan=pc.ma_tai_khoan
JOIN nhan_vien nv ON nv.ma_nhan_vien=tk.ma_nhan_vien
WHERE pc.ma_vai_tro='store_manager' AND pc.pham_vi='store'
AND pc.trang_thai='active' AND pc.thu_hoi_luc IS NULL AND pc.tu_ngay<=UTC_TIMESTAMP(6)
AND (pc.den_ngay IS NULL OR UTC_TIMESTAMP(6)<pc.den_ngay);

-- 8. Hiển thị các sản phẩm trong từng phiếu phân phối, kèm tên cửa hàng và số lượng phân phối.
select pp.ma_phan_phoi as 'Phiếu phân phối',
       ch.ten_cua_hang as 'Cửa hàng', sp.ten_san_pham as 'Sản phẩm',
       sp.mau_sac as 'Màu sắc', sp.kich_co as 'Kích cỡ',
       sp.mau_sac as 'Màu sắc', sp.kich_co as 'Kích cỡ',
       ctpp.so_luong as 'Số lượng'
from v_chi_tiet_phan_phoi as ctpp
join v_san_pham as sp on ctpp.ma_san_pham = sp.ma_san_pham
join v_phan_phoi as pp on ctpp.ma_phan_phoi = pp.ma_phan_phoi
join cua_hang as ch on pp.ma_cua_hang = ch.ma_cua_hang;

-- MỨC 3 - GOM NHÓM, THỐNG KÊ VÀ TRUY VẤN LỒNG NHAU
-- 9. Báo cáo 5 sản phẩm bán tốt năm 2026 (chỉ lấy sản phẩm bán từ 20 đơn vị trở lên).
select sp.ma_san_pham as 'Mã sản phẩm', sp.ten_san_pham as 'Sản phẩm',
       sp.mau_sac as 'Màu sắc',
       sp.kich_co as 'Kích cỡ',
       sum(ctdh.so_luong) as 'Số lượng đã bán',
       sum((ctdh.so_luong * ctdh.don_gia_ban - ctdh.giam_gia)) as 'Tổng doanh thu'
from v_don_hang as dh
join v_chi_tiet_don_hang as ctdh on ctdh.ma_don_hang = dh.ma_don_hang
join v_san_pham as sp on sp.ma_san_pham = ctdh.ma_san_pham
where dh.ngay_tao_don >= '2026-01-01' and dh.ngay_tao_don < '2027-01-01'
group by ctdh.ma_san_pham
    having sum(ctdh.so_luong) >= 20
order by sum((ctdh.so_luong * ctdh.don_gia_ban - ctdh.giam_gia)) desc,
         sum(ctdh.so_luong) desc,
         sp.ma_san_pham
limit 5;

-- 10. Tính tổng số lượng phân phối theo từng cửa hàng và sản phẩm.
select ch.ten_cua_hang as 'Cửa hàng',
       sp.ten_san_pham as 'Sản phẩm',
       sp.mau_sac as 'Màu sắc', sp.kich_co as 'Kích cỡ',
       sum(ctpp.so_luong) as 'Số lượng'
from v_chi_tiet_phan_phoi as ctpp
join v_phan_phoi as pp on ctpp.ma_phan_phoi = pp.ma_phan_phoi
join cua_hang as ch on pp.ma_cua_hang = ch.ma_cua_hang
join v_san_pham as sp on sp.ma_san_pham = ctpp.ma_san_pham
group by ch.ma_cua_hang,  sp.ma_san_pham
order by ch.ten_cua_hang, sp.ten_san_pham;

-- 11. Tính số lượng hàng còn lại của của hàng CH001
SELECT k.ma_cua_hang,k.ma_kho,t.ma_san_pham,s.ten_san_pham,s.mau_sac,s.kich_co,t.so_luong
FROM ton_kho t JOIN kho k ON k.ma_kho=t.ma_kho
JOIN v_san_pham s ON s.ma_san_pham=t.ma_san_pham
WHERE k.ma_cua_hang='CH001' ORDER BY k.ma_kho,t.ma_san_pham;

-- 12. In ra các nhân viên có tổng doanh thu cao nhất của từng cửa hàng
with doanh_thu as (
    select ch.ma_cua_hang,
           ch.ten_cua_hang, nv.ma_nhan_vien,
           nv.ho_ten,
           sum((ctdh.so_luong * ctdh.don_gia_ban - ctdh.giam_gia)) as doanh_thu_nv
    from v_nhan_vien as nv
    join v_don_hang as dh on nv.ma_nhan_vien = dh.ma_nhan_vien
    join cua_hang as ch on dh.ma_cua_hang = ch.ma_cua_hang
    join v_chi_tiet_don_hang as ctdh on dh.ma_don_hang = ctdh.ma_don_hang
    join v_san_pham as sp on ctdh.ma_san_pham = sp.ma_san_pham
    group by ch.ma_cua_hang, nv.ma_nhan_vien
)
select dt.ten_cua_hang as 'Cửa hàng',
       dt.ho_ten as 'Họ tên',
       dt.doanh_thu_nv as 'Doanh thu'
from doanh_thu as dt
where dt.doanh_thu_nv = (
    select max(dt2.doanh_thu_nv)
    from doanh_thu as dt2
    where dt2.ma_cua_hang = dt.ma_cua_hang
)
order by dt.ma_cua_hang;

-- 13. xếp hạng doanh thu các cửa hàng khu vực miền Bắc
with doanh_thu_cua_hang as (
    select ch.ma_cua_hang,
           ch.ten_cua_hang,
           sum((ctdh.so_luong * ctdh.don_gia_ban - ctdh.giam_gia)) as tong_doanh_thu
    from v_chi_tiet_don_hang as ctdh
    join v_san_pham as sp on ctdh.ma_san_pham = sp.ma_san_pham
    join v_don_hang as dh on ctdh.ma_don_hang = dh.ma_don_hang
    join v_nhan_vien as nv on dh.ma_nhan_vien = nv.ma_nhan_vien
    join cua_hang as ch on dh.ma_cua_hang = ch.ma_cua_hang
    group by ch.ma_cua_hang
)
select dtch.ma_cua_hang, ch.dia_chi, dtch.tong_doanh_thu,
    dense_rank() over (order by dtch.tong_doanh_thu desc) as 'Xếp hạng'
from doanh_thu_cua_hang as dtch
join cua_hang as ch on dtch.ma_cua_hang = ch.ma_cua_hang
where ch.khu_vuc = 1
order by 'Xếp hạng' desc;

-- 14. Nhân viên có doanh thu trên 3000000 theo cửa hàng giao dịch
SELECT dh.ma_cua_hang,nv.ma_nhan_vien,nv.ho_ten,
SUM(ct.so_luong*ct.don_gia_ban-ct.giam_gia) AS doanh_thu
FROM v_don_hang dh JOIN nhan_vien nv ON nv.ma_nhan_vien=dh.ma_nhan_vien
JOIN v_chi_tiet_don_hang ct ON ct.ma_don_hang=dh.ma_don_hang
GROUP BY dh.ma_cua_hang,nv.ma_nhan_vien,nv.ho_ten
HAVING SUM(ct.so_luong*ct.don_gia_ban-ct.giam_gia)>3000000;


-- 15. In ra các cửa hàng có tỉ lệ khách quay lại trong năm 2026 > 0
with so_khach as (
    select dh.ma_cua_hang, count(distinct dh.ma_khach_hang) as tong_khach
    from v_don_hang as dh
    join v_nhan_vien as nv on dh.ma_nhan_vien = nv.ma_nhan_vien
    where dh.ngay_tao_don >= '2026-01-01' and dh.ngay_tao_don < '2027-01-01'
    group by dh.ma_cua_hang
),
so_khach_quay_lai as (
    select khach_hang_lap_lai.ma_cua_hang, count(*) as khach_quay_lai
    from (
        select dh.ma_cua_hang, dh.ma_khach_hang
        from v_don_hang as dh
        join v_nhan_vien as nv on dh.ma_nhan_vien = nv.ma_nhan_vien
        where dh.ngay_tao_don >= '2026-01-01' and dh.ngay_tao_don < '2027-01-01'
        group by dh.ma_cua_hang, dh.ma_khach_hang
            having count(distinct dh.ma_don_hang) >= 2
    ) as khach_hang_lap_lai
    group by khach_hang_lap_lai.ma_cua_hang
)
select sk.ma_cua_hang as 'Mã cửa hàng',
       sk.tong_khach as 'Tổng khách hàng',
       skql.khach_quay_lai as 'Số khách quay lại',
       round(skql.khach_quay_lai * 100.0 / sk.tong_khach, 2) as 'Tỉ lệ khách quay lại (%)'
from so_khach as sk
left join so_khach_quay_lai as skql on sk.ma_cua_hang = skql.ma_cua_hang
where skql.khach_quay_lai > 0
order by sk.ma_cua_hang;

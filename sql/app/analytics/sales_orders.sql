SELECT dh.ma_don_hang, dh.ngay_tao_don, dh.ma_khach_hang,
       ch.ten_cua_hang, COALESCE(ct.quantity, 0) AS quantity,
       COALESCE(ct.revenue, 0) AS revenue
FROM don_hang AS dh
JOIN nhan_vien AS nv ON nv.ma_nhan_vien = dh.ma_nhan_vien
JOIN cua_hang AS ch ON ch.ma_cua_hang = nv.ma_cua_hang
LEFT JOIN (
    SELECT ma_don_hang,
           SUM(so_luong) AS quantity,
           SUM(so_luong * don_gia_ban) AS revenue
    FROM chi_tiet_don_hang
    GROUP BY ma_don_hang
) AS ct ON ct.ma_don_hang = dh.ma_don_hang
WHERE (
    %(actor_role)s = 'admin'
    OR (%(actor_role)s = 'regional_manager' AND ch.khu_vuc = %(actor_region)s)
    OR (%(actor_role)s = 'store_manager' AND ch.ma_cua_hang = %(actor_store)s)
)
ORDER BY dh.ngay_tao_don DESC, dh.ma_don_hang DESC
LIMIT 50;

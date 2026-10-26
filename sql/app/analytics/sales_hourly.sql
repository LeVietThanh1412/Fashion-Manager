SELECT HOUR(dh.ngay_tao_don) AS hour, COUNT(*) AS count
FROM don_hang AS dh
JOIN nhan_vien AS nv ON nv.ma_nhan_vien = dh.ma_nhan_vien
JOIN cua_hang AS ch ON ch.ma_cua_hang = nv.ma_cua_hang
WHERE dh.ngay_tao_don >= %(start)s AND dh.ngay_tao_don < %(end)s
  AND (
      %(actor_role)s = 'admin'
      OR (%(actor_role)s = 'regional_manager' AND ch.khu_vuc = %(actor_region)s)
      OR (%(actor_role)s = 'store_manager' AND ch.ma_cua_hang = %(actor_store)s)
  )
GROUP BY HOUR(dh.ngay_tao_don);

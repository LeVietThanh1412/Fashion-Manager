SELECT ch.ma_cua_hang, ch.ten_cua_hang, ch.dia_chi, ch.so_dien_thoai,
       ch.email, ch.khu_vuc
FROM cua_hang AS ch
WHERE %(actor_role)s = 'admin'
   OR (%(actor_role)s = 'regional_manager'
       AND ch.khu_vuc = %(actor_region)s)
   OR (%(actor_role)s = 'store_manager'
       AND ch.ma_cua_hang = %(actor_store)s)
ORDER BY ten_cua_hang, ma_cua_hang;

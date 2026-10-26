SELECT ma_cua_hang, ten_cua_hang, khu_vuc
FROM cua_hang
WHERE %(actor_role)s = 'admin'
   OR (%(actor_role)s = 'regional_manager' AND khu_vuc = %(actor_region)s)
   OR (%(actor_role)s = 'store_manager' AND ma_cua_hang = %(actor_store)s)
ORDER BY ten_cua_hang, ma_cua_hang;

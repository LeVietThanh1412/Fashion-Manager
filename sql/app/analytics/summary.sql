SELECT
    (SELECT COUNT(*) FROM san_pham) AS total_products,
    (SELECT COUNT(*) FROM danh_muc) AS total_categories,
    (
        SELECT COUNT(*)
        FROM cua_hang AS ch
        WHERE %(actor_role)s = 'admin'
           OR (%(actor_role)s = 'regional_manager'
               AND ch.khu_vuc = %(actor_region)s)
           OR (%(actor_role)s = 'store_manager'
               AND ch.ma_cua_hang = %(actor_store)s)
    ) AS total_stores,
    (
        SELECT COUNT(*)
        FROM don_hang AS dh
        JOIN nhan_vien AS nv ON nv.ma_nhan_vien = dh.ma_nhan_vien
        JOIN cua_hang AS ch ON ch.ma_cua_hang = nv.ma_cua_hang
        WHERE %(actor_role)s = 'admin'
           OR (%(actor_role)s = 'regional_manager'
               AND ch.khu_vuc = %(actor_region)s)
           OR (%(actor_role)s = 'store_manager'
               AND ch.ma_cua_hang = %(actor_store)s)
    ) AS total_orders;

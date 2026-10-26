UPDATE nhan_vien
SET quyen_han = 'staff',
    khu_vuc_quan_ly = NULL,
    ma_cua_hang = COALESCE(%(store_id)s, ma_cua_hang)
WHERE ma_nhan_vien = %(employee_id)s
  AND quyen_han IN ('regional_manager', 'store_manager')
  AND trang_thai = 'active'
  AND (
      (%(actor_role)s = 'admin')
      OR (%(actor_role)s = 'regional_manager'
          AND quyen_han = 'store_manager'
          AND EXISTS (
              SELECT 1
              FROM cua_hang AS ch
              WHERE ch.ma_cua_hang = nhan_vien.ma_cua_hang
                AND ch.khu_vuc = %(actor_region)s
          ))
  );

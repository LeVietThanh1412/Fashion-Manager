UPDATE nhan_vien
SET luong = %(salary)s
WHERE ma_nhan_vien = %(employee_id)s
  AND trang_thai = 'active'
  AND (
      (%(actor_role)s = 'admin' AND quyen_han <> 'admin')
      OR (%(actor_role)s = 'regional_manager'
          AND quyen_han IN ('store_manager', 'staff')
          AND EXISTS (
              SELECT 1
              FROM cua_hang AS ch
              WHERE ch.ma_cua_hang = nhan_vien.ma_cua_hang
                AND ch.khu_vuc = %(actor_region)s
          ))
      OR (%(actor_role)s = 'store_manager'
          AND quyen_han = 'staff'
          AND ma_cua_hang = %(actor_store)s)
  );

SELECT khu_vuc
FROM cua_hang
WHERE ma_cua_hang = %(store_id)s
LIMIT 1;

SELECT gia_ban
FROM san_pham
WHERE ma_san_pham = %(product_id)s
LIMIT 1;

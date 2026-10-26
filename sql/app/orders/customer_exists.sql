SELECT ma_khach_hang
FROM khach_hang
WHERE ma_khach_hang = %(customer_id)s
LIMIT 1;

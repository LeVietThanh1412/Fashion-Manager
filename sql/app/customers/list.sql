SELECT ma_khach_hang, ho_ten, so_dien_thoai
FROM khach_hang
WHERE (%(search)s IS NULL OR ho_ten LIKE CONCAT('%', %(search)s, '%'))
ORDER BY ho_ten, ma_khach_hang
LIMIT %(limit)s OFFSET %(offset)s;

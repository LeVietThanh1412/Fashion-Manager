SELECT ma_san_pham, ma_danh_muc, ten_san_pham, mau_sac, kich_co, gia_ban
FROM san_pham
WHERE (%(search)s IS NULL OR ten_san_pham LIKE CONCAT('%', %(search)s, '%'))
  AND (%(category_id)s IS NULL OR ma_danh_muc = %(category_id)s)
ORDER BY ten_san_pham, ma_san_pham
LIMIT %(limit)s OFFSET %(offset)s;

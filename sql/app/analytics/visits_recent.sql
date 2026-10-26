SELECT id, thoi_gian, trang_vao, ip_an_danh, thiet_bi, den_tu
FROM luot_truy_cap_web
WHERE thoi_gian >= %(start)s AND thoi_gian < %(end)s
ORDER BY thoi_gian DESC, id DESC
LIMIT 50;

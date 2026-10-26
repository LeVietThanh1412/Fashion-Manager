INSERT INTO luot_truy_cap_web
    (thoi_gian, trang_vao, ip_an_danh, thiet_bi, den_tu)
VALUES (UTC_TIMESTAMP(), %(path)s, %(ip)s, %(device)s, %(referrer)s);

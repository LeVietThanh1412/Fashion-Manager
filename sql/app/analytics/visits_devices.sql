SELECT thiet_bi AS device, COUNT(*) AS count
FROM luot_truy_cap_web
WHERE thoi_gian >= %(start)s AND thoi_gian < %(end)s
GROUP BY thiet_bi;

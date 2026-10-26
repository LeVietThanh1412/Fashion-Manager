SELECT HOUR(DATE_ADD(thoi_gian, INTERVAL 7 HOUR)) AS hour, COUNT(*) AS count
FROM luot_truy_cap_web
WHERE thoi_gian >= %(start)s AND thoi_gian < %(end)s
GROUP BY hour;

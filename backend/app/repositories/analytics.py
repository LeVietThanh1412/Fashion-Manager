from datetime import datetime, time, timedelta, timezone

from app.db.connection import connection

VIETNAM = timezone(timedelta(hours=7))


def record_visit(path: str, ip: str, device: str, referrer: str) -> None:
    with connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO luot_truy_cap_web (thoi_gian, trang_vao, ip_an_danh, thiet_bi, den_tu) VALUES (UTC_TIMESTAMP(), %s, %s, %s, %s)',
                (path, ip, device, referrer),
            )
            conn.commit()
        finally:
            cursor.close()


def get_visit_dashboard(now: datetime | None = None) -> dict:
    today = (now or datetime.now(timezone.utc)).astimezone(VIETNAM).date()
    first = today - timedelta(days=29)
    start = datetime.combine(first, time.min, VIETNAM).astimezone(timezone.utc).replace(tzinfo=None)
    end = datetime.combine(today + timedelta(days=1), time.min, VIETNAM).astimezone(timezone.utc).replace(tzinfo=None)
    condition = ' FROM luot_truy_cap_web WHERE thoi_gian >= %s AND thoi_gian < %s '
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT DATE(DATE_ADD(thoi_gian, INTERVAL 7 HOUR)) AS day, COUNT(*) AS count' + condition + 'GROUP BY day', (start, end))
            days = {str(row['day']): int(row['count']) for row in cursor.fetchall()}
            cursor.execute('SELECT HOUR(DATE_ADD(thoi_gian, INTERVAL 7 HOUR)) AS hour, COUNT(*) AS count' + condition + 'GROUP BY hour', (start, end))
            hours = {int(row['hour']): int(row['count']) for row in cursor.fetchall()}
            cursor.execute('SELECT thiet_bi AS device, COUNT(*) AS count' + condition + 'GROUP BY thiet_bi', (start, end))
            devices = {row['device']: int(row['count']) for row in cursor.fetchall()}
            cursor.execute('SELECT id, thoi_gian, trang_vao, ip_an_danh, thiet_bi, den_tu' + condition + 'ORDER BY thoi_gian DESC, id DESC LIMIT 50', (start, end))
            visits = [
                {
                    'id': row['id'],
                    'timestamp': row['thoi_gian'].replace(tzinfo=timezone.utc).isoformat(),
                    'path': row['trang_vao'], 'ip': row['ip_an_danh'],
                    'device': row['thiet_bi'], 'referrer': row['den_tu'],
                    'location': None,
                }
                for row in cursor.fetchall()
            ]
        finally:
            cursor.close()
    daily = [{'date': (first + timedelta(days=i)).isoformat(), 'count': days.get(str(first + timedelta(days=i)), 0)} for i in range(30)]
    return {
        'timezone': 'Asia/Ho_Chi_Minh', 'total': sum(row['count'] for row in daily),
        'daily': daily, 'hourly': [{'hour': hour, 'count': hours.get(hour, 0)} for hour in range(24)],
        'devices': {device: devices.get(device, 0) for device in ('mobile', 'tablet', 'desktop')},
        'visits': visits,
    }

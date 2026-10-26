from datetime import datetime, time, timedelta, timezone
from pathlib import Path

from app.db.connection import connection
from app.db.query_loader import QueryLoader

VIETNAM = timezone(timedelta(hours=7))
SQL_ROOT = Path(__file__).resolve().parents[3] / "sql" / "app"
loader = QueryLoader(SQL_ROOT)


def record_visit(path: str, ip: str, device: str, referrer: str) -> None:
    with connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                loader.load("analytics/visit_create.sql"),
                {"path": path, "ip": ip, "device": device, "referrer": referrer},
            )
            conn.commit()
        finally:
            cursor.close()


def get_visit_dashboard(now: datetime | None = None) -> dict:
    today = (now or datetime.now(timezone.utc)).astimezone(VIETNAM).date()
    first = today - timedelta(days=29)
    start = datetime.combine(first, time.min, VIETNAM).astimezone(timezone.utc).replace(tzinfo=None)
    end = datetime.combine(today + timedelta(days=1), time.min, VIETNAM).astimezone(timezone.utc).replace(tzinfo=None)
    period = {"start": start, "end": end}
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(loader.load("analytics/visits_daily.sql"), period)
            days = {str(row['day']): int(row['count']) for row in cursor.fetchall()}
            cursor.execute(loader.load("analytics/visits_hourly.sql"), period)
            hours = {int(row['hour']): int(row['count']) for row in cursor.fetchall()}
            cursor.execute(loader.load("analytics/visits_devices.sql"), period)
            devices = {row['device']: int(row['count']) for row in cursor.fetchall()}
            cursor.execute(loader.load("analytics/visits_recent.sql"), period)
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

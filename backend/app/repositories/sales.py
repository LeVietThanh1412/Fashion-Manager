from datetime import datetime, time, timedelta, timezone

from app.db.connection import connection

VIETNAM = timezone(timedelta(hours=7))


def get_sales_dashboard(now: datetime | None = None) -> dict:
    # Business DATETIME values represent the shop's local Vietnam time.
    today = (now or datetime.now(timezone.utc)).astimezone(VIETNAM).date()
    first = today - timedelta(days=29)
    period = (datetime.combine(first, time.min), datetime.combine(today + timedelta(days=1), time.min))
    totals = '(SELECT ma_don_hang, SUM(so_luong * don_gia_ban) AS revenue, SUM(so_luong) AS quantity FROM chi_tiet_don_hang GROUP BY ma_don_hang)'
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                'SELECT DATE(dh.ngay_tao_don) AS day, COUNT(*) AS count, COALESCE(SUM(ct.revenue), 0) AS revenue '
                f'FROM don_hang dh LEFT JOIN {totals} ct ON ct.ma_don_hang = dh.ma_don_hang '
                'WHERE dh.ngay_tao_don >= %s AND dh.ngay_tao_don < %s GROUP BY day', period,
            )
            days = {str(row['day']): row for row in cursor.fetchall()}
            cursor.execute('SELECT HOUR(ngay_tao_don) AS hour, COUNT(*) AS count FROM don_hang WHERE ngay_tao_don >= %s AND ngay_tao_don < %s GROUP BY hour', period)
            hours = {int(row['hour']): int(row['count']) for row in cursor.fetchall()}
            cursor.execute(
                'SELECT dm.ma_danh_muc AS id, dm.ten_danh_muc AS name, COUNT(sp.ma_san_pham) AS count '
                'FROM danh_muc dm LEFT JOIN san_pham sp ON sp.ma_danh_muc = dm.ma_danh_muc '
                'GROUP BY dm.ma_danh_muc, dm.ten_danh_muc ORDER BY count DESC, dm.ma_danh_muc'
            )
            categories = [{'id': row['id'], 'name': row['name'], 'count': int(row['count'])} for row in cursor.fetchall()]
            cursor.execute(
                'SELECT dh.ma_don_hang, dh.ngay_tao_don, dh.ma_khach_hang, ch.ten_cua_hang, '
                'COALESCE(ct.quantity, 0) AS quantity, COALESCE(ct.revenue, 0) AS revenue '
                f'FROM don_hang dh LEFT JOIN {totals} ct ON ct.ma_don_hang = dh.ma_don_hang '
                'JOIN nhan_vien nv ON nv.ma_nhan_vien = dh.ma_nhan_vien '
                'JOIN cua_hang ch ON ch.ma_cua_hang = nv.ma_cua_hang '
                'ORDER BY dh.ngay_tao_don DESC, dh.ma_don_hang DESC LIMIT 50'
            )
            orders = [{
                'id': row['ma_don_hang'], 'timestamp': row['ngay_tao_don'].replace(tzinfo=VIETNAM).isoformat(),
                'customer_id': row['ma_khach_hang'], 'store': row['ten_cua_hang'],
                'quantity': int(row['quantity']), 'total': int(row['revenue']),
            } for row in cursor.fetchall()]
        finally:
            cursor.close()
    daily = []
    for index in range(30):
        day = (first + timedelta(days=index)).isoformat()
        row = days.get(day, {})
        daily.append({'date': day, 'count': int(row.get('count', 0)), 'revenue': int(row.get('revenue', 0))})
    return {
        'timezone': 'Asia/Ho_Chi_Minh', 'total_orders': sum(row['count'] for row in daily),
        'total_revenue': sum(row['revenue'] for row in daily), 'daily': daily,
        'hourly': [{'hour': hour, 'count': hours.get(hour, 0)} for hour in range(24)],
        'categories': categories, 'orders': orders,
    }

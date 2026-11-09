from datetime import datetime,time,timedelta,timezone
from app.db.connection import connection
from app.permissions import store_scope

VIETNAM=timezone(timedelta(hours=7))
_TOTALS="""(SELECT ma_don_hang,SUM(so_luong) AS quantity,
SUM(so_luong*don_gia_ban-giam_gia) AS revenue
FROM chi_tiet_don_hang GROUP BY ma_don_hang)"""
_BASE=f"FROM don_hang dh LEFT JOIN cua_hang ch ON ch.ma_cua_hang=dh.ma_cua_hang LEFT JOIN {_TOTALS} ct ON ct.ma_don_hang=dh.ma_don_hang"
_DAILY_SQL=f"SELECT DATE(dh.ngay_tao_don) AS day,COUNT(*) AS count,SUM(ct.revenue) AS revenue {_BASE} WHERE dh.trang_thai<>'cancelled' AND dh.ngay_tao_don >= %s AND dh.ngay_tao_don < %s AND {{scope}} GROUP BY DATE(dh.ngay_tao_don)"
_RECENT_ORDERS_SQL=f"SELECT dh.ma_don_hang,dh.ngay_tao_don,dh.ma_khach_hang,ch.ten_cua_hang,ct.quantity,ct.revenue {_BASE} WHERE dh.trang_thai<>'cancelled' AND {{scope}} ORDER BY dh.ngay_tao_don DESC,dh.ma_don_hang DESC LIMIT 50"


def get_sales_dashboard(actor,now=None):
    today=(now or datetime.now(timezone.utc)).astimezone(VIETNAM).date()
    condition,scope=store_scope(actor,permission='reports.read')
    mode='current'
    with connection() as conn:
        cursor=conn.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT MAX(dh.ngay_tao_don) AS latest_order_at {_BASE} WHERE dh.trang_thai<>'cancelled' AND {condition}",scope)
            latest=cursor.fetchone()['latest_order_at']
            if latest:
                today=latest.date()
                mode='latest_order'
            first=today-timedelta(days=29)
            start,end=datetime.combine(first,time.min),datetime.combine(today+timedelta(days=1),time.min)
            cursor.execute(_DAILY_SQL.format(scope=condition),[start,end,*scope])
            days={str(row['day']):row for row in cursor.fetchall()}
            cursor.execute(f"SELECT HOUR(dh.ngay_tao_don) AS hour,COUNT(*) AS count {_BASE} WHERE dh.trang_thai<>'cancelled' AND dh.ngay_tao_don >= %s AND dh.ngay_tao_don < %s AND {condition} GROUP BY HOUR(dh.ngay_tao_don)",[start,end,*scope])
            hours={int(row['hour']):int(row['count']) for row in cursor.fetchall()}
            cursor.execute('SELECT dm.ma_danh_muc AS id,dm.ten_danh_muc AS name,COUNT(s.ma_san_pham) AS count FROM danh_muc dm LEFT JOIN mau_san_pham m ON m.ma_danh_muc=dm.ma_danh_muc LEFT JOIN san_pham s ON s.ma_mau=m.ma_mau GROUP BY dm.ma_danh_muc,dm.ten_danh_muc ORDER BY dm.ma_danh_muc')
            categories=cursor.fetchall()
            cursor.execute(_RECENT_ORDERS_SQL.format(scope=condition),scope)
            orders=[{'id':r['ma_don_hang'],'timestamp':r['ngay_tao_don'].replace(tzinfo=VIETNAM).isoformat(),'customer_id':r['ma_khach_hang'],'store':r['ten_cua_hang'],'quantity':int(r['quantity'] or 0),'total':r['revenue']} for r in cursor.fetchall()]
        finally:
            cursor.close()
    daily=[]
    for i in range(30):
        day=(first+timedelta(days=i)).isoformat()
        row=days.get(day,{})
        daily.append({'date':day,'count':int(row.get('count',0)),'revenue':row.get('revenue',0) or 0})
    return {'timezone':'Asia/Ho_Chi_Minh','period':{'start':first.isoformat(),'end':today.isoformat(),'mode':mode},
            'total_orders':sum(r['count'] for r in daily),'total_revenue':sum(r['revenue'] for r in daily),
            'daily':daily,'hourly':[{'hour':h,'count':hours.get(h,0)} for h in range(24)],'categories':categories,'orders':orders}

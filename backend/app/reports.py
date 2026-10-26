from datetime import datetime, time, timedelta, timezone

from app.db.helpers import rows
from app.documents import document_scope, list_documents
from app.permissions import require_role, store_scope

VIETNAM = timezone(timedelta(hours=7))
ORDER_TOTALS = '(SELECT ma_don_hang,SUM(so_luong) AS quantity,SUM(so_luong*don_gia_ban) AS revenue FROM chi_tiet_don_hang GROUP BY ma_don_hang)'
SALES_BASE = (f'FROM don_hang d JOIN nhan_vien nv ON nv.ma_nhan_vien=d.ma_nhan_vien '
              f'JOIN cua_hang ch ON ch.ma_cua_hang=nv.ma_cua_hang JOIN {ORDER_TOTALS} ct ON ct.ma_don_hang=d.ma_don_hang')


def summary(actor):
    condition, params = store_scope(actor)
    order_condition, order_params = document_scope('orders', actor)
    return {
        'total_products': rows('SELECT COUNT(*) AS n FROM san_pham')[0]['n'],
        'total_categories': rows('SELECT COUNT(*) AS n FROM danh_muc')[0]['n'],
        'total_stores': rows(f'SELECT COUNT(*) AS n FROM cua_hang ch WHERE {condition}', params)[0]['n'],
        'total_orders': rows(f'SELECT COUNT(*) AS n {SALES_BASE} WHERE {order_condition}', order_params)[0]['n'],
    }


def dashboard(actor):
    today = datetime.now(VIETNAM).date()
    first = today - timedelta(days=29)
    condition, params = document_scope('orders', actor)
    period = [datetime.combine(first, time.min), datetime.combine(today+timedelta(days=1), time.min)]
    where = f'{condition} AND d.ngay_tao_don >= %s AND d.ngay_tao_don < %s'
    daily_rows = rows(f'SELECT DATE(d.ngay_tao_don) AS day,COUNT(*) AS count,SUM(ct.revenue) AS revenue {SALES_BASE} WHERE {where} GROUP BY day', [*params,*period])
    days = {str(row['day']): row for row in daily_rows}
    hours = rows(f'SELECT HOUR(d.ngay_tao_don) AS hour,COUNT(*) AS count {SALES_BASE} WHERE {where} GROUP BY hour', [*params,*period])
    daily = []
    for index in range(30):
        day = (first+timedelta(days=index)).isoformat()
        row = days.get(day, {})
        daily.append({'date':day, 'count':row.get('count',0), 'revenue':row.get('revenue',0)})
    latest = list_documents('orders', actor, limit=50)['items']
    return {
        'total_orders':sum(row['count'] for row in daily),
        'total_revenue':sum(row['revenue'] for row in daily), 'daily':daily,
        'hourly':[{'hour':h,'count':next((r['count'] for r in hours if r['hour']==h),0)} for h in range(24)],
        'categories':rows('SELECT dm.ma_danh_muc AS id,dm.ten_danh_muc AS name,COUNT(sp.ma_san_pham) AS count FROM danh_muc dm LEFT JOIN san_pham sp ON sp.ma_danh_muc=dm.ma_danh_muc GROUP BY dm.ma_danh_muc,dm.ten_danh_muc ORDER BY count DESC,dm.ma_danh_muc'),
        'orders':[{'id':o['ma_don_hang'],'timestamp':o['ngay_tao_don'].replace(tzinfo=VIETNAM).isoformat(),
                   'customer_id':o['ma_khach_hang'],'store':o['ten_cua_hang'],'quantity':o['tong_so_luong'],'total':o['tong_tien']} for o in latest],
    }


def business_report(actor, start, end, group):
    require_role(actor,'admin','regional_manager','store_manager')
    groups = {
        'day': ('DATE(d.ngay_tao_don)', 'DATE_FORMAT(d.ngay_tao_don,\'%d/%m/%Y\')'),
        'month': ("DATE_FORMAT(d.ngay_tao_don,'%Y-%m')", "DATE_FORMAT(d.ngay_tao_don,'%m/%Y')"),
        'store': ('ch.ma_cua_hang','ch.ten_cua_hang'),
        'employee': ('nv.ma_nhan_vien','nv.ho_ten'),
        'region': ('ch.khu_vuc', "CASE ch.khu_vuc WHEN 1 THEN 'Miền Bắc' WHEN 2 THEN 'Miền Trung' ELSE 'Miền Nam' END"),
    }
    key, label = groups[group]
    condition, params = store_scope(actor)
    period_where = 'DATE(d.ngay_tao_don) BETWEEN %s AND %s'
    sales = rows(f'SELECT {key} AS ma,{label} AS ten,COUNT(*) AS so_don,SUM(ct.quantity) AS so_luong,SUM(ct.revenue) AS doanh_thu {SALES_BASE} WHERE {condition} AND {period_where} GROUP BY {key},{label} ORDER BY ma', [*params,start,end])
    distributions = rows(f'SELECT ch.ma_cua_hang,ch.ten_cua_hang,COUNT(DISTINCT pp.ma_phan_phoi) AS so_phieu,COALESCE(SUM(ct.so_luong),0) AS so_luong FROM phan_phoi pp JOIN nhan_vien nv ON nv.ma_nhan_vien=pp.ma_nhan_vien JOIN cua_hang ch ON ch.ma_cua_hang=nv.ma_cua_hang JOIN chi_tiet_phan_phoi ct ON ct.ma_phan_phoi=pp.ma_phan_phoi WHERE {condition} AND pp.ngay_phan_phoi BETWEEN %s AND %s GROUP BY ch.ma_cua_hang,ch.ten_cua_hang ORDER BY ch.ma_cua_hang', [*params,start,end])
    products = rows(f'SELECT sp.ma_san_pham,sp.ten_san_pham,SUM(line.so_luong) AS so_luong,SUM(line.so_luong*line.don_gia_ban) AS doanh_thu FROM don_hang d JOIN nhan_vien nv ON nv.ma_nhan_vien=d.ma_nhan_vien JOIN cua_hang ch ON ch.ma_cua_hang=nv.ma_cua_hang JOIN chi_tiet_don_hang line ON line.ma_don_hang=d.ma_don_hang JOIN san_pham sp ON sp.ma_san_pham=line.ma_san_pham WHERE {condition} AND {period_where} GROUP BY sp.ma_san_pham,sp.ten_san_pham ORDER BY so_luong DESC,sp.ma_san_pham LIMIT 20', [*params,start,end])
    return {'sales':sales,'distributions':distributions,'products':products,
            'total_orders':sum(r['so_don'] for r in sales),'total_revenue':sum(r['doanh_thu'] for r in sales)}

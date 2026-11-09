"""Sales reports use immutable order stores and saved historical prices."""
from app.repositories.sales import get_sales_dashboard as dashboard
from app.repositories.catalog import get_catalog_summary as summary
from app.permissions import require_permission,store_scope
from app.db.helpers import rows


def business_report(actor,start,end,group):
    require_permission(actor,'reports.read')
    groups={'day':'DATE(d.ngay_tao_don)','month':"DATE_FORMAT(d.ngay_tao_don,'%Y-%m')",
            'store':'d.ma_cua_hang','employee':'d.ma_nhan_vien','region':'ch.khu_vuc'}
    key=groups[group]
    condition,params=store_scope(actor,permission='reports.read')
    return {'sales':rows(f"""SELECT {key} AS ma,COUNT(DISTINCT d.ma_don_hang) AS so_don,
        SUM(ct.so_luong) AS so_luong,
        COALESCE(SUM(ct.so_luong*ct.don_gia_ban-ct.giam_gia),0) AS doanh_thu
        FROM don_hang d LEFT JOIN cua_hang ch ON ch.ma_cua_hang=d.ma_cua_hang
        LEFT JOIN chi_tiet_don_hang ct ON ct.ma_don_hang=d.ma_don_hang
        WHERE d.trang_thai<>'cancelled' AND DATE(d.ngay_tao_don) BETWEEN %s AND %s AND {condition}
        GROUP BY {key} ORDER BY ma""",[start,end,*params])}

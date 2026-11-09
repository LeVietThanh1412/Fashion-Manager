from app.db.helpers import rows
from app.permissions import store_scope, has_system_permission


def list_products(search=None, category_id=None, limit=20, offset=0):
    return rows("""SELECT s.ma_san_pham,s.ma_san_pham AS ma_sku,s.ma_mau,
        m.ma_danh_muc,m.ten_san_pham,s.mau_sac,s.kich_co,s.gia_san_pham AS gia_ban
        FROM san_pham s JOIN mau_san_pham m ON m.ma_mau=s.ma_mau
        WHERE s.trang_thai='active' AND m.trang_thai='active'
        AND (%s IS NULL OR m.ten_san_pham LIKE CONCAT('%%',%s,'%%'))
        AND (%s IS NULL OR m.ma_danh_muc=%s)
        ORDER BY m.ten_san_pham,s.ma_san_pham LIMIT %s OFFSET %s""",
        [search,search,category_id,category_id,limit,offset])


def list_stores(actor, permission='stores.read'):
    condition, params = store_scope(actor,permission=permission)
    return rows(f"SELECT ch.*,kv.ten_khu_vuc FROM cua_hang ch JOIN khu_vuc kv ON kv.ma_khu_vuc=ch.khu_vuc WHERE ch.trang_thai='active' AND {condition} ORDER BY ch.ma_cua_hang",params)


def list_categories():
    return rows('SELECT * FROM danh_muc ORDER BY ten_danh_muc')


def list_regions(actor):
    if has_system_permission(actor,'stores.read'):
        return rows('SELECT * FROM khu_vuc ORDER BY ma_khu_vuc')
    condition, params = store_scope(actor)
    return rows(f'SELECT DISTINCT kv.* FROM khu_vuc kv JOIN cua_hang ch ON ch.khu_vuc=kv.ma_khu_vuc WHERE {condition} ORDER BY kv.ma_khu_vuc',params)


def list_customers_for_orders(actor):
    condition, params = store_scope(actor,permission='customers.read')
    if has_system_permission(actor,'customers.read'):
        return rows('SELECT * FROM khach_hang ORDER BY ho_ten LIMIT 500')
    return rows(f"SELECT k.* FROM khach_hang k WHERE EXISTS (SELECT 1 FROM don_hang d JOIN cua_hang ch ON ch.ma_cua_hang=d.ma_cua_hang WHERE d.ma_khach_hang=k.ma_khach_hang AND {condition}) ORDER BY k.ho_ten LIMIT 500",params)


def get_catalog_summary(actor):
    condition, params = store_scope(actor,permission='reports.read')
    return rows(f"""SELECT (SELECT COUNT(*) FROM san_pham) AS total_products,
        (SELECT COUNT(*) FROM danh_muc) AS total_categories,
        (SELECT COUNT(*) FROM cua_hang ch WHERE {condition}) AS total_stores,
        (SELECT COUNT(*) FROM don_hang d LEFT JOIN cua_hang ch ON ch.ma_cua_hang=d.ma_cua_hang
            WHERE d.trang_thai<>'cancelled' AND {condition}) AS total_orders""",[*params,*params])[0]

"""CRUD các bảng đơn; bảng và cột chỉ được lấy từ danh sách cố định."""
from fastapi import HTTPException

from app.db.helpers import rows, transaction
from app.permissions import check_store, require_role, store_scope

TABLES = {
    'categories': ('danh_muc', 'ma_danh_muc'),
    'products': ('san_pham', 'ma_san_pham'),
    'stores': ('cua_hang', 'ma_cua_hang'),
    'customers': ('khach_hang', 'ma_khach_hang'),
}


def list_catalog(resource, actor, search='', limit=20, offset=0):
    params = []
    if resource == 'categories':
        sql = ('SELECT dm.*, (SELECT COUNT(*) FROM san_pham sp WHERE sp.ma_danh_muc=dm.ma_danh_muc) AS so_san_pham '
               'FROM danh_muc dm WHERE CONCAT_WS(\' \',dm.ma_danh_muc,dm.ten_danh_muc) LIKE %s')
        params = [f'%{search}%']
        key = 'dm.ma_danh_muc'
    elif resource == 'products':
        sql = ("SELECT sp.*, dm.ten_danh_muc FROM san_pham sp JOIN danh_muc dm ON dm.ma_danh_muc=sp.ma_danh_muc "
               "WHERE CONCAT_WS(' ',sp.ma_san_pham,sp.ten_san_pham,sp.mau_sac,sp.kich_co,dm.ten_danh_muc) LIKE %s")
        params = [f'%{search}%']
        key = 'sp.ma_san_pham'
    elif resource == 'stores':
        condition, params = store_scope(actor)
        sql = f"SELECT ch.* FROM cua_hang ch WHERE {condition} AND CONCAT_WS(' ',ch.ma_cua_hang,ch.ten_cua_hang,ch.dia_chi) LIKE %s"
        params.append(f'%{search}%')
        key = 'ch.ma_cua_hang'
    else:
        sql = "SELECT * FROM khach_hang WHERE CONCAT_WS(' ',ma_khach_hang,ho_ten,so_dien_thoai) LIKE %s"
        params = [f'%{search}%']
        key = 'ma_khach_hang'
    count = rows(f'SELECT COUNT(*) AS total FROM ({sql}) AS filtered', params)[0]['total']
    items = rows(f'{sql} ORDER BY {key} LIMIT %s OFFSET %s', [*params, limit, offset])
    return {'items': items, 'total': count, 'limit': limit, 'offset': offset}


def save_catalog(resource, actor, data, record_id=None):
    table, pk = TABLES[resource]
    if resource != 'customers':
        require_role(actor, 'admin')
    if record_id and data[pk] != record_id:
        raise HTTPException(400, 'Không được thay đổi mã định danh.')
    with transaction() as cursor:
        if record_id:
            cursor.execute(f'SELECT * FROM {table} WHERE {pk}=%s FOR UPDATE', (record_id,))
            old = cursor.fetchone()
            if not old:
                raise HTTPException(404, 'Không tìm thấy dữ liệu.')
            if resource == 'stores' and old['khu_vuc'] != data['khu_vuc']:
                raise HTTPException(400, 'Phạm vi bài toán chưa xét chuyển cửa hàng sang khu vực khác.')
            columns = [key for key in data if key != pk]
            cursor.execute(f"UPDATE {table} SET {','.join(key+'=%s' for key in columns)} WHERE {pk}=%s",
                           [*[data[key] for key in columns], record_id])
        else:
            cursor.execute(f"INSERT INTO {table} ({','.join(data)}) VALUES ({','.join(['%s']*len(data))})", list(data.values()))
    return data


def delete_catalog(resource, actor, record_id):
    require_role(actor, 'admin')
    table, pk = TABLES[resource]
    with transaction() as cursor:
        cursor.execute(f'DELETE FROM {table} WHERE {pk}=%s', (record_id,))
        if not cursor.rowcount:
            raise HTTPException(404, 'Không tìm thấy dữ liệu.')
    return {'message': 'Đã xóa dữ liệu.'}

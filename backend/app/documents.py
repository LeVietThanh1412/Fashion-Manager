"""Đơn hàng và phiếu phân phối được lưu cả đầu phiếu và chi tiết trong một transaction."""
from fastapi import HTTPException

from app.db.helpers import rows, transaction
from app.permissions import check_employee, check_store, require_role, store_scope

KINDS = {
    'orders': ('don_hang','ma_don_hang','chi_tiet_don_hang','ngay_tao_don'),
    'distributions': ('phan_phoi','ma_phan_phoi','chi_tiet_phan_phoi','ngay_phan_phoi'),
}


def document_scope(kind, actor):
    condition, params = store_scope(actor)
    if kind == 'orders' and actor['quyen_han'] == 'staff':
        condition += ' AND d.ma_nhan_vien=%s'
        params.append(actor['ma_nhan_vien'])
    return condition, params


def document_base(kind):
    table, pk, detail, date_column = KINDS[kind]
    return (f'FROM {table} d JOIN nhan_vien nv ON nv.ma_nhan_vien=d.ma_nhan_vien '
            'JOIN cua_hang ch ON ch.ma_cua_hang=nv.ma_cua_hang'), pk, detail, date_column


def list_documents(kind, actor, search='', limit=20, offset=0, start=None, end=None, customer=None):
    base, pk, detail, date_column = document_base(kind)
    condition, params = document_scope(kind, actor)
    condition += f" AND CONCAT_WS(' ',d.{pk},nv.ho_ten,ch.ten_cua_hang) LIKE %s"
    params.append(f'%{search}%')
    if start:
        condition += f' AND DATE(d.{date_column}) >= %s'
        params.append(start)
    if end:
        condition += f' AND DATE(d.{date_column}) <= %s'
        params.append(end)
    if customer and kind == 'orders':
        condition += ' AND d.ma_khach_hang=%s'
        params.append(customer)
    total = rows(f'SELECT COUNT(*) AS total {base} WHERE {condition}', params)[0]['total']
    amount = f', (SELECT SUM(ct.so_luong*ct.don_gia_ban) FROM {detail} ct WHERE ct.{pk}=d.{pk}) AS tong_tien' if kind == 'orders' else ''
    sql = (f'SELECT d.*,nv.ho_ten AS ten_nhan_vien,ch.ten_cua_hang,ch.ma_cua_hang,ch.ma_cua_hang AS cua_hang_giao_dich,'
           f'(SELECT SUM(ct.so_luong) FROM {detail} ct WHERE ct.{pk}=d.{pk}) AS tong_so_luong {amount} '
           f'{base} WHERE {condition} ORDER BY d.{date_column} DESC,d.{pk} DESC LIMIT %s OFFSET %s')
    return {'items': rows(sql, [*params, limit, offset]), 'total': total}


def get_document(kind, actor, record_id):
    base, pk, detail, date_column = document_base(kind)
    condition, params = document_scope(kind, actor)
    with transaction() as cursor:
        cursor.execute(f'SELECT d.*,ch.ten_cua_hang,ch.ma_cua_hang,ch.ma_cua_hang AS cua_hang_giao_dich,nv.ho_ten AS ten_nhan_vien {base} WHERE d.{pk}=%s AND {condition}', [record_id, *params])
        document = cursor.fetchone()
        if not document:
            raise HTTPException(404, 'Không tìm thấy phiếu trong phạm vi của bạn.')
        amount = ',ct.so_luong*ct.don_gia_ban AS thanh_tien' if kind == 'orders' else ''
        cursor.execute(f'SELECT ct.*,sp.ten_san_pham,sp.mau_sac,sp.kich_co,sp.gia_san_pham {amount} FROM {detail} ct JOIN san_pham sp ON sp.ma_san_pham=ct.ma_san_pham WHERE ct.{pk}=%s ORDER BY ct.ma_san_pham', (record_id,))
        document['chi_tiet'] = cursor.fetchall()
        if kind == 'orders':
            document['tong_tien'] = sum(line['thanh_tien'] for line in document['chi_tiet'])
    return document


def save_document(kind, actor, data, record_id=None):
    table, pk, detail, date_column = KINDS[kind]
    if kind == 'distributions':
        require_role(actor, 'admin', 'regional_manager')
    if record_id and data[pk] != record_id:
        raise HTTPException(400, 'Không được thay đổi mã phiếu.')
    lines = data['chi_tiet']
    header = {key:value for key,value in data.items() if key != 'chi_tiet'}
    if kind == 'distributions':
        # Cửa hàng chỉ là lựa chọn trên form; dữ liệu lưu được suy ra từ người nhận.
        header.pop('ma_cua_hang')
    with transaction() as cursor:
        old_prices = {}
        if record_id:
            base, _, _, _ = document_base(kind)
            condition, params = document_scope(kind, actor)
            cursor.execute(f'SELECT d.* {base} WHERE d.{pk}=%s AND {condition} FOR UPDATE', [record_id, *params])
            old = cursor.fetchone()
            if not old:
                raise HTTPException(404, 'Không tìm thấy phiếu trong phạm vi của bạn.')
            if old['ma_nhan_vien'] != data['ma_nhan_vien']:
                raise HTTPException(400, 'Không thay người lập/nhận của phiếu đã lưu.')
            if kind == 'orders':
                cursor.execute(f'SELECT ma_san_pham,don_gia_ban FROM {detail} WHERE {pk}=%s', (record_id,))
                old_prices = {row['ma_san_pham']: row['don_gia_ban'] for row in cursor.fetchall()}
        employee = check_employee(cursor, actor, data['ma_nhan_vien'])
        if not employee['ma_cua_hang'] or employee['trang_thai'] != 'active':
            raise HTTPException(400, 'Nhân viên lập/nhận phải đang làm việc tại một cửa hàng.')
        if actor['quyen_han'] == 'staff' and employee['ma_nhan_vien'] != actor['ma_nhan_vien']:
            raise HTTPException(403, 'Nhân viên chỉ lập đơn dưới tên mình.')
        if kind == 'distributions':
            check_store(cursor, actor, data['ma_cua_hang'])
            if employee['ma_cua_hang'] != data['ma_cua_hang']:
                raise HTTPException(400, 'Nhân viên nhận hàng phải thuộc cửa hàng nhận.')
        else:
            check_store(cursor, actor, employee['ma_cua_hang'])
        prepared = []
        for line in lines:
            cursor.execute('SELECT gia_san_pham FROM san_pham WHERE ma_san_pham=%s', (line['ma_san_pham'],))
            product = cursor.fetchone()
            if not product:
                raise HTTPException(400, f"Sản phẩm {line['ma_san_pham']} không tồn tại.")
            item = [data[pk], line['ma_san_pham'], line['so_luong']]
            if kind == 'orders':
                price = line.get('don_gia_ban')
                if price is None:
                    price = old_prices.get(line['ma_san_pham'], product['gia_san_pham'])
                item.append(price)
            prepared.append(item)
        if record_id:
            columns = [key for key in header if key != pk]
            cursor.execute(f"UPDATE {table} SET {','.join(key+'=%s' for key in columns)} WHERE {pk}=%s", [*[header[key] for key in columns], record_id])
            cursor.execute(f'DELETE FROM {detail} WHERE {pk}=%s', (record_id,))
        else:
            cursor.execute(f"INSERT INTO {table} ({','.join(header)}) VALUES ({','.join(['%s']*len(header))})", list(header.values()))
        columns = f'{pk},ma_san_pham,so_luong' + (',don_gia_ban' if kind == 'orders' else '')
        placeholders = ','.join(['%s']*len(prepared[0]))
        cursor.executemany(f'INSERT INTO {detail} ({columns}) VALUES ({placeholders})', prepared)
    return get_document(kind, actor, data[pk])


def delete_document(kind, actor, record_id):
    if kind == 'distributions':
        require_role(actor, 'admin', 'regional_manager')
    table, pk, detail, _ = KINDS[kind]
    base, _, _, _ = document_base(kind)
    condition, params = document_scope(kind, actor)
    with transaction() as cursor:
        cursor.execute(f'SELECT d.{pk} {base} WHERE d.{pk}=%s AND {condition} FOR UPDATE', [record_id, *params])
        if not cursor.fetchone():
            raise HTTPException(404, 'Không tìm thấy phiếu trong phạm vi của bạn.')
        cursor.execute(f'DELETE FROM {detail} WHERE {pk}=%s', (record_id,))
        cursor.execute(f'DELETE FROM {table} WHERE {pk}=%s', (record_id,))
    return {'message':'Đã xóa phiếu và các dòng chi tiết.'}

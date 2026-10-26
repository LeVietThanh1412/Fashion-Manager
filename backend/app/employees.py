"""Nhân sự: cấp trên chỉ được sửa cấp dưới trong đúng phạm vi."""
from fastapi import HTTPException

from app.db.helpers import rows, transaction
from app.permissions import check_employee, check_store, require_role, store_scope

RANK = {'staff': 1, 'store_manager': 2, 'regional_manager': 3, 'admin': 4}
EMPLOYEE_FIELDS = ('ma_nhan_vien,ho_ten,so_dien_thoai,email,ma_cua_hang,ma_quan_ly,'
                   'quyen_han,khu_vuc_quan_ly,luong,cap_bac,trang_thai')


def list_employees(actor, search='', limit=20, offset=0):
    require_role(actor, 'admin', 'regional_manager', 'store_manager')
    condition, params = store_scope(actor)
    # Regional managers can also see their own profile; no other region's manager.
    condition = f'({condition} OR nv.ma_nhan_vien=%s)'
    params.append(actor['ma_nhan_vien'])
    where = f"{condition} AND CONCAT_WS(' ',nv.ma_nhan_vien,nv.ho_ten,nv.email) LIKE %s"
    params.append(f'%{search}%')
    base = 'FROM nhan_vien nv LEFT JOIN cua_hang ch ON ch.ma_cua_hang=nv.ma_cua_hang '
    total = rows(f'SELECT COUNT(*) AS total {base} WHERE {where}', params)[0]['total']
    select = ','.join('nv.'+f for f in EMPLOYEE_FIELDS.split(','))
    items = rows(f'SELECT {select},ch.ten_cua_hang {base} WHERE {where} ORDER BY nv.ma_nhan_vien LIMIT %s OFFSET %s', [*params, limit, offset])
    return {'items': items, 'total': total}


def can_manage(actor, target):
    if actor['ma_nhan_vien'] == target['ma_nhan_vien']:
        raise HTTPException(403, 'Không tự thay đổi quyền hoặc lương của bản thân.')
    if RANK[actor['quyen_han']] <= RANK[target['quyen_han']]:
        raise HTTPException(403, 'Chỉ được quản lý người có cấp quyền thấp hơn.')


def validate_assignment(cursor, actor, data, employee_id):
    if RANK[data['quyen_han']] >= RANK[actor['quyen_han']]:
        raise HTTPException(403, 'Chỉ được bổ nhiệm vai trò thấp hơn cấp quyền của mình.')
    if data['ma_cua_hang']:
        check_store(cursor, actor, data['ma_cua_hang'])
    if data.get('ma_quan_ly'):
        if data['ma_quan_ly'] == employee_id:
            raise HTTPException(400, 'Nhân viên không thể tự quản lý mình.')
        cursor.execute('SELECT * FROM nhan_vien WHERE ma_nhan_vien=%s', (data['ma_quan_ly'],))
        manager = cursor.fetchone()
        if not manager or manager['trang_thai'] != 'active' or RANK[manager['quyen_han']] <= RANK[data['quyen_han']]:
            raise HTTPException(400, 'Người quản lý phải đang làm việc và có cấp quyền cao hơn.')
        if manager['quyen_han'] == 'store_manager' and manager['ma_cua_hang'] != data['ma_cua_hang']:
            raise HTTPException(400, 'Quản lý trực tiếp phải thuộc cùng cửa hàng.')
        if manager['quyen_han'] == 'regional_manager':
            store = check_store(cursor, actor, data['ma_cua_hang']) if data['ma_cua_hang'] else None
            if not store or store['khu_vuc'] != manager['khu_vuc_quan_ly']:
                raise HTTPException(400, 'Quản lý trực tiếp phải phụ trách đúng khu vực.')


def close_history(cursor, employee_id):
    cursor.execute('UPDATE lich_su_quan_ly SET den_ngay=CURRENT_TIMESTAMP WHERE ma_nhan_vien=%s AND den_ngay IS NULL', (employee_id,))


def save_employee(actor, data, employee_id=None):
    require_role(actor, 'admin', 'regional_manager', 'store_manager')
    if employee_id and employee_id != data['ma_nhan_vien']:
        raise HTTPException(400, 'Không được thay đổi mã nhân viên.')
    new_id = data['ma_nhan_vien']
    with transaction() as cursor:
        # Serialize appointments so two people cannot take the same position.
        cursor.execute("SELECT ma_nhan_vien FROM nhan_vien WHERE quyen_han='admin' FOR UPDATE")
        cursor.fetchall()
        old = check_employee(cursor, actor, employee_id) if employee_id else None
        if old:
            can_manage(actor, old)
        validate_assignment(cursor, actor, data, new_id)
        if old:
            if old['ma_cua_hang'] != data['ma_cua_hang']:
                cursor.execute('SELECT ma_don_hang FROM don_hang WHERE ma_nhan_vien=%s LIMIT 1', (employee_id,))
                sold = cursor.fetchone()
                cursor.execute('SELECT ma_phan_phoi FROM phan_phoi WHERE ma_nhan_vien=%s LIMIT 1', (employee_id,))
                received = cursor.fetchone()
                if sold or received:
                    raise HTTPException(400, 'Nhân viên đã có giao dịch; không đổi cửa hàng để giữ đúng lịch sử.')
                cursor.execute('SELECT ma_nhan_vien FROM nhan_vien WHERE ma_quan_ly=%s LIMIT 1', (employee_id,))
                if cursor.fetchone():
                    raise HTTPException(400, 'Hãy bổ nhiệm người thay thế trước khi chuyển quản lý sang cửa hàng khác.')
        if old and data['trang_thai'] == 'inactive' and old['quyen_han'] in ('regional_manager', 'store_manager'):
            cursor.execute("SELECT ma_nhan_vien FROM nhan_vien WHERE ma_quan_ly=%s AND trang_thai='active' LIMIT 1", (new_id,))
            if cursor.fetchone():
                raise HTTPException(400, 'Hãy bổ nhiệm người thay thế trước khi cho quản lý nghỉ việc.')
        if data['quyen_han'] in ('store_manager', 'regional_manager') and data['trang_thai'] == 'active':
            column = 'ma_cua_hang' if data['quyen_han'] == 'store_manager' else 'khu_vuc_quan_ly'
            cursor.execute(f"SELECT * FROM nhan_vien WHERE quyen_han=%s AND {column}=%s AND trang_thai='active' AND ma_nhan_vien<>%s",
                           (data['quyen_han'], data[column], new_id))
            displaced = cursor.fetchall()
            for previous in displaced:
                can_manage(actor, previous)
                close_history(cursor, previous['ma_nhan_vien'])
                if previous['quyen_han'] == 'store_manager':
                    cursor.execute("UPDATE nhan_vien SET quyen_han='staff',ma_quan_ly=NULL WHERE ma_nhan_vien=%s", (previous['ma_nhan_vien'],))
                else:
                    cursor.execute("UPDATE nhan_vien SET trang_thai='inactive' WHERE ma_nhan_vien=%s", (previous['ma_nhan_vien'],))
        columns = list(data)
        if old:
            columns.remove('ma_nhan_vien')
            cursor.execute(f"UPDATE nhan_vien SET {','.join(c+'=%s' for c in columns)} WHERE ma_nhan_vien=%s", [*[data[c] for c in columns], new_id])
        else:
            cursor.execute(f"INSERT INTO nhan_vien ({','.join(columns)}) VALUES ({','.join(['%s']*len(columns))})", [data[c] for c in columns])
        changed = not old or any(old[c] != data[c] for c in ('quyen_han','ma_cua_hang','khu_vuc_quan_ly','trang_thai'))
        if changed:
            close_history(cursor, new_id)
            if data['quyen_han'] in ('regional_manager','store_manager') and data['trang_thai'] == 'active':
                cursor.execute('INSERT INTO lich_su_quan_ly (ma_nhan_vien,quyen_han,ma_cua_hang,khu_vuc_quan_ly) VALUES (%s,%s,%s,%s)',
                               (new_id, data['quyen_han'], data['ma_cua_hang'], data['khu_vuc_quan_ly']))
        if data['trang_thai'] == 'active' and data['quyen_han'] == 'store_manager':
            cursor.execute("UPDATE nhan_vien SET ma_quan_ly=%s WHERE ma_cua_hang=%s AND quyen_han='staff'", (new_id, data['ma_cua_hang']))
        elif data['trang_thai'] == 'active' and data['quyen_han'] == 'regional_manager':
            cursor.execute("UPDATE nhan_vien nv JOIN cua_hang ch ON ch.ma_cua_hang=nv.ma_cua_hang SET nv.ma_quan_ly=%s WHERE ch.khu_vuc=%s AND nv.quyen_han='store_manager'", (new_id, data['khu_vuc_quan_ly']))
        if old and changed and old['quyen_han'] in ('regional_manager','store_manager') and old['quyen_han'] != data['quyen_han']:
            # Demotion keeps subordinates connected to the next senior manager.
            cursor.execute('UPDATE nhan_vien SET ma_quan_ly=%s WHERE ma_quan_ly=%s AND ma_nhan_vien<>%s', (data['ma_quan_ly'], new_id, new_id))
    return data


def delete_employee(actor, employee_id):
    require_role(actor, 'admin', 'regional_manager', 'store_manager')
    with transaction() as cursor:
        employee = check_employee(cursor, actor, employee_id)
        can_manage(actor, employee)
        cursor.execute('DELETE FROM nhan_vien WHERE ma_nhan_vien=%s', (employee_id,))
    return {'message': 'Đã xóa nhân viên. Với nhân viên đã có giao dịch, hãy chọn Ngừng làm việc.'}


def history(actor):
    require_role(actor, 'admin', 'regional_manager', 'store_manager')
    condition, params = store_scope(actor)
    if actor['quyen_han'] == 'regional_manager':
        condition = f'({condition} OR ls.khu_vuc_quan_ly=%s)'
        params.append(actor['khu_vuc_quan_ly'])
    return {'items': rows(f'SELECT ls.*,nv.ho_ten,ch.ten_cua_hang FROM lich_su_quan_ly ls JOIN nhan_vien nv ON nv.ma_nhan_vien=ls.ma_nhan_vien LEFT JOIN cua_hang ch ON ch.ma_cua_hang=ls.ma_cua_hang WHERE {condition} ORDER BY ls.tu_ngay DESC,ls.ma_lich_su DESC', params)}

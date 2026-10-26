"""Phân quyền đơn giản cho BTL: nhận mã nhân viên, đọc vai trò từ CSDL."""
from fastapi import HTTPException

ROLES = {
    'admin': 'Chủ thương hiệu',
    'regional_manager': 'Quản lý khu vực',
    'store_manager': 'Quản lý cửa hàng',
    'staff': 'Nhân viên bán hàng',
}


def require_role(actor, *roles):
    if actor['quyen_han'] not in roles:
        raise HTTPException(403, 'Vai trò của bạn không được thực hiện thao tác này.')


def store_scope(actor, alias='ch'):
    """Trả điều kiện WHERE và tham số theo phạm vi người đang sử dụng."""
    role = actor['quyen_han']
    if role == 'admin':
        return '1=1', []
    if role == 'regional_manager':
        return f'{alias}.khu_vuc = %s', [actor['khu_vuc_quan_ly']]
    return f'{alias}.ma_cua_hang = %s', [actor['ma_cua_hang']]


def check_store(cursor, actor, store_id):
    condition, params = store_scope(actor)
    cursor.execute(f'SELECT ch.* FROM cua_hang ch WHERE ch.ma_cua_hang=%s AND {condition}', [store_id, *params])
    store = cursor.fetchone()
    if not store:
        raise HTTPException(403, 'Cửa hàng không thuộc phạm vi được phân công.')
    return store


def check_employee(cursor, actor, employee_id):
    cursor.execute('SELECT * FROM nhan_vien WHERE ma_nhan_vien=%s', (employee_id,))
    employee = cursor.fetchone()
    if not employee:
        raise HTTPException(404, 'Không tìm thấy nhân viên.')
    if actor['quyen_han'] != 'admin':
        check_store(cursor, actor, employee['ma_cua_hang'])
    return employee

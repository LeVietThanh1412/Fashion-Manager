from fastapi import HTTPException
from app.db.helpers import rows, transaction
from app.permissions import check_store, check_employee, employee_scope
from app.repositories.catalog import list_stores as scoped_stores
from app.core.phone import normalize_phone
import mysql.connector

# Current workplace is for presentation only. Permission checks use EXISTS over history.
_FIELDS = """nv.*,
    (SELECT MIN(lv.ma_cua_hang) FROM phan_cong_lam_viec lv WHERE lv.ma_nhan_vien=nv.ma_nhan_vien AND lv.tu_ngay<=UTC_TIMESTAMP() AND (lv.den_ngay IS NULL OR UTC_TIMESTAMP()<lv.den_ngay)) AS current_store,
    (SELECT GROUP_CONCAT(DISTINCT CONCAT(cv.ten_chuc_vu,' @ ',COALESCE(ch.ten_cua_hang,k.ten_kho)) SEPARATOR ', ') FROM phan_cong_lam_viec lv JOIN chuc_vu cv ON cv.ma_chuc_vu=lv.ma_chuc_vu LEFT JOIN cua_hang ch ON ch.ma_cua_hang=lv.ma_cua_hang LEFT JOIN kho k ON k.ma_kho=lv.ma_kho WHERE lv.ma_nhan_vien=nv.ma_nhan_vien AND lv.tu_ngay<=UTC_TIMESTAMP() AND (lv.den_ngay IS NULL OR UTC_TIMESTAMP()<lv.den_ngay)) AS positions_workplaces,
    (SELECT GROUP_CONCAT(DISTINCT pc.ma_vai_tro ORDER BY pc.ma_vai_tro) FROM tai_khoan tk JOIN phan_cong_quyen pc ON pc.ma_tai_khoan=tk.ma_tai_khoan WHERE tk.ma_nhan_vien=nv.ma_nhan_vien AND pc.trang_thai='active' AND pc.thu_hoi_luc IS NULL AND pc.tu_ngay<=UTC_TIMESTAMP(6) AND (pc.den_ngay IS NULL OR UTC_TIMESTAMP(6)<pc.den_ngay)) AS roles"""


def _display(row):
    row['ma_cua_hang'] = row.pop('current_store')
    row['quyen_han'] = row.get('roles') or 'unassigned'
    row['ten_cua_hang'] = row['ma_cua_hang']
    row['khu_vuc_quan_ly'] = None
    return row


def list_employees(actor):
    condition, params = employee_scope(actor)
    return [_display(row) for row in rows(f'SELECT {_FIELDS} FROM nhan_vien nv WHERE {condition} ORDER BY nv.ho_ten,nv.ma_nhan_vien',params)]


def get_employee(employee_id, actor, permission='employees.read'):
    with transaction() as cursor:
        return check_employee(cursor,actor,employee_id,permission)


def list_stores(actor):
    return scoped_stores(actor,'employees.write')


def create_employee(employee, actor):
    try:
        phone=normalize_phone(employee['phone'])
    except ValueError as exc:
        raise HTTPException(422,str(exc)) from None
    try:
        with transaction() as cursor:
            check_store(cursor,actor,employee['store_id'],'employees.write')
            cursor.execute('SELECT ma_chuc_vu FROM chuc_vu WHERE ma_chuc_vu=%s',[employee['position_id']])
            if not cursor.fetchone():
                raise HTTPException(422,'Unknown position.')
            cursor.execute("""INSERT INTO nhan_vien (ma_nhan_vien,ho_ten,so_dien_thoai,email,ma_quan_ly,luong)
                VALUES (%s,%s,%s,%s,%s,%s)""",[employee['employee_id'],employee['name'],phone,employee['email'],actor['ma_nhan_vien'],employee['salary']])
            cursor.execute('INSERT INTO phan_cong_lam_viec (ma_nhan_vien,ma_chuc_vu,ma_cua_hang) VALUES (%s,%s,%s)',[employee['employee_id'],employee['position_id'],employee['store_id']])
    except mysql.connector.IntegrityError as exc:
        if exc.errno==1062:
            raise HTTPException(409,'Employee ID, canonical phone or email already exists.') from None
        raise


def update_salary(employee_id, salary, actor):
    with transaction() as cursor:
        check_employee(cursor,actor,employee_id,'employees.salary')
        if actor['ma_nhan_vien']==employee_id:
            raise HTTPException(403,'Cannot edit your own salary.')
        cursor.execute('UPDATE nhan_vien SET luong=%s WHERE ma_nhan_vien=%s',[salary,employee_id])
    return True


def set_employee_status(employee_id, status, actor):
    with transaction() as cursor:
        check_employee(cursor,actor,employee_id,'employees.write')
        if actor['ma_nhan_vien']==employee_id:
            raise HTTPException(403,'Cannot deactivate yourself.')
        cursor.execute('UPDATE nhan_vien SET trang_thai=%s WHERE ma_nhan_vien=%s',[status,employee_id])
        if status=='inactive':
            cursor.execute("UPDATE tai_khoan SET trang_thai='locked',auth_version=auth_version+1 WHERE ma_nhan_vien=%s",[employee_id])
        # Reactivating personnel never unlocks a login or re-grants a role.
    return True


def delete_employee(employee_id, actor):
    return set_employee_status(employee_id,'inactive',actor)


def transfer_work(employee_id, store_id, actor):
    with transaction() as cursor:
        check_employee(cursor,actor,employee_id,'employees.write')
        check_store(cursor,actor,store_id,'employees.write')
        cursor.execute('SELECT ma_nhan_vien FROM nhan_vien WHERE ma_nhan_vien=%s FOR UPDATE',[employee_id])
        cursor.fetchone()
        cursor.execute('SELECT ma_cua_hang,ma_kho,ma_chuc_vu FROM phan_cong_lam_viec WHERE ma_nhan_vien=%s AND (den_ngay IS NULL OR den_ngay>UTC_TIMESTAMP())',[employee_id])
        placements=cursor.fetchall()
        from app.permissions import check_warehouse
        for placement in placements:
            if placement['ma_cua_hang']:
                check_store(cursor,actor,placement['ma_cua_hang'],'employees.write')
            else:
                check_warehouse(cursor,actor,placement['ma_kho'],'employees.write')
        cursor.execute('UPDATE phan_cong_lam_viec SET den_ngay=UTC_TIMESTAMP() WHERE ma_nhan_vien=%s AND den_ngay IS NULL AND tu_ngay<UTC_TIMESTAMP()',[employee_id])
        cursor.execute('SELECT ma_phan_cong FROM phan_cong_lam_viec WHERE ma_nhan_vien=%s AND den_ngay IS NULL',[employee_id])
        if cursor.fetchall():
            raise HTTPException(409,'Review same-second or future work placements first.')
        position=placements[0]['ma_chuc_vu'] if placements else 'sales'
        cursor.execute('INSERT INTO phan_cong_lam_viec (ma_nhan_vien,ma_chuc_vu,ma_cua_hang) VALUES (%s,%s,%s)',[employee_id,position,store_id])
    return {'status':'transferred'}


def get_distribution(actor):
    from app.repositories.inventory import list_inventory
    return list_inventory(actor)

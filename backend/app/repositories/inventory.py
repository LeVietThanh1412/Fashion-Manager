from uuid import uuid4
from fastapi import HTTPException
from app.db.helpers import rows, transaction
from app.permissions import warehouse_scope, check_warehouse


def list_warehouses(actor):
    condition, params = warehouse_scope(actor)
    return rows(f"SELECT k.* FROM kho k WHERE k.trang_thai='active' AND {condition} ORDER BY k.ma_kho",params)


def list_inventory(actor):
    condition, params = warehouse_scope(actor)
    return rows(f'''SELECT t.*,t.ma_san_pham AS ma_sku,m.ten_san_pham,s.mau_sac,s.kich_co
        FROM ton_kho t JOIN kho k ON k.ma_kho=t.ma_kho
        JOIN san_pham s ON s.ma_san_pham=t.ma_san_pham JOIN mau_san_pham m ON m.ma_mau=s.ma_mau
        WHERE {condition} ORDER BY t.ma_kho,t.ma_san_pham''',params)


def movements(actor):
    condition, params = warehouse_scope(actor)
    return rows(f'''SELECT b.* FROM bien_dong_kho b JOIN kho k ON k.ma_kho=b.ma_kho
        WHERE {condition} ORDER BY b.ma_bien_dong DESC LIMIT 500''',params)


def lock_stock(cursor, pairs, allow_inactive=False):
    # Every stock writer takes locks in the same order, including transfer reversals.
    for warehouse, sku in sorted(set(pairs)):
        status='' if allow_inactive else " AND s.trang_thai='active' AND m.trang_thai='active'"
        cursor.execute('SELECT s.ma_san_pham FROM san_pham s JOIN mau_san_pham m ON m.ma_mau=s.ma_mau WHERE s.ma_san_pham=%s'+status, [sku])
        if not cursor.fetchone():
            raise HTTPException(404,'SKU inactive or missing: '+sku)
        cursor.execute('INSERT INTO ton_kho (ma_kho,ma_san_pham,so_luong) VALUES (%s,%s,0) ON DUPLICATE KEY UPDATE so_luong=so_luong',[warehouse,sku])
        cursor.execute('SELECT so_luong FROM ton_kho WHERE ma_kho=%s AND ma_san_pham=%s FOR UPDATE',[warehouse,sku])
        cursor.fetchone()


def change_stock(cursor, actor, warehouse, sku, quantity, kind, reason, order=None, transfer=None):
    cursor.execute('UPDATE ton_kho SET so_luong=so_luong+%s WHERE ma_kho=%s AND ma_san_pham=%s AND so_luong+%s>=0', [quantity,warehouse,sku,quantity])
    if cursor.rowcount != 1:
        raise HTTPException(409,'Insufficient stock for SKU '+sku)
    cursor.execute('''INSERT INTO bien_dong_kho
        (ma_kho,ma_san_pham,so_luong,loai,ly_do,ma_tai_khoan,ma_don_hang,ma_phan_phoi)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''', [warehouse,sku,quantity,kind,reason,actor['ma_tai_khoan'],order,transfer])


def adjust_stock(actor, warehouse, sku, quantity, reason):
    with transaction() as cursor:
        check_warehouse(cursor,actor,warehouse,'inventory.adjust')
        lock_stock(cursor,[(warehouse,sku)])
        change_stock(cursor,actor,warehouse,sku,quantity,'adjustment',reason)
    return {'status':'adjusted'}


def transfer_stock(actor, source, target, details):
    if source == target:
        raise HTTPException(422,'Source and destination must differ.')
    code = 'PP'+uuid4().hex[:18]
    with transaction() as cursor:
        check_warehouse(cursor,actor,source,'inventory.transfer')
        destination = check_warehouse(cursor,actor,target,'inventory.transfer')
        lock_stock(cursor,[(w,d['product_id']) for w in (source,target) for d in details])
        cursor.execute('''INSERT INTO phan_phoi (ma_phan_phoi,ma_nhan_vien,ma_cua_hang,ma_kho_nguon,ma_kho_dich,ngay_phan_phoi,trang_thai)
            VALUES (%s,%s,%s,%s,%s,CURRENT_DATE(),'completed')''', [code,actor['ma_nhan_vien'],destination['ma_cua_hang'],source,target])
        for line in details:
            sku, quantity = line['product_id'], line['quantity']
            cursor.execute('INSERT INTO chi_tiet_phan_phoi VALUES (%s,%s,%s)',[code,sku,quantity])
            change_stock(cursor,actor,source,sku,-quantity,'transfer','Transfer out',transfer=code)
            change_stock(cursor,actor,target,sku,quantity,'transfer','Transfer in',transfer=code)
    return {'transfer_id':code,'status':'completed'}


def cancel_transfer(actor, transfer_id):
    with transaction() as cursor:
        cursor.execute('SELECT * FROM phan_phoi WHERE ma_phan_phoi=%s FOR UPDATE',[transfer_id])
        header = cursor.fetchone()
        if not header:
            raise HTTPException(404,'Transfer not found.')
        source, target = header['ma_kho_nguon'], header['ma_kho_dich']
        if not source or not target:
            raise HTTPException(409,'Legacy distribution needs review.')
        check_warehouse(cursor,actor,source,'inventory.transfer')
        check_warehouse(cursor,actor,target,'inventory.transfer')
        if header['trang_thai']=='cancelled':
            return {'status':'cancelled'}
        if header['trang_thai']!='completed':
            raise HTTPException(409,'Transfer needs review.')
        cursor.execute('SELECT * FROM chi_tiet_phan_phoi WHERE ma_phan_phoi=%s',[transfer_id])
        details = cursor.fetchall()
        lock_stock(cursor,[(w,d['ma_san_pham']) for w in (source,target) for d in details],allow_inactive=True)
        for line in details:
            sku, quantity = line['ma_san_pham'], line['so_luong']
            change_stock(cursor,actor,target,sku,-quantity,'cancel_transfer','Cancel transfer',transfer=transfer_id)
            change_stock(cursor,actor,source,sku,quantity,'cancel_transfer','Cancel transfer',transfer=transfer_id)
        cursor.execute("UPDATE phan_phoi SET trang_thai='cancelled' WHERE ma_phan_phoi=%s",[transfer_id])
    return {'status':'cancelled'}

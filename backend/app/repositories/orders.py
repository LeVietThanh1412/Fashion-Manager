from datetime import datetime,timedelta,timezone
from uuid import uuid4
from fastapi import HTTPException
from app.db.helpers import rows,transaction
from app.permissions import store_scope,check_store
from app.repositories.inventory import lock_stock,change_stock

VIETNAM=timezone(timedelta(hours=7))


def create_order(actor,customer_id,details,store_id=None,warehouse_id=None):
    order_id='DH'+uuid4().hex[:18]
    with transaction() as cursor:
        if not store_id:
            condition,params=store_scope(actor,permission='sales.create')
            cursor.execute(f"SELECT ch.ma_cua_hang FROM cua_hang ch WHERE ch.trang_thai='active' AND {condition}",params)
            stores=cursor.fetchall()
            if len(stores)!=1:
                raise HTTPException(422,'Select the sales store explicitly.')
            store_id=stores[0]['ma_cua_hang']
        check_store(cursor,actor,store_id,'sales.create')
        cursor.execute("SELECT ma_kho FROM kho WHERE ma_cua_hang=%s AND trang_thai='active' ORDER BY ma_kho",[store_id])
        warehouses=[row['ma_kho'] for row in cursor.fetchall()]
        if warehouse_id is None and len(warehouses)==1:
            warehouse_id=warehouses[0]
        if warehouse_id not in warehouses:
            raise HTTPException(422,'Select an active warehouse belonging to the sales store.')
        cursor.execute('SELECT ma_khach_hang FROM khach_hang WHERE ma_khach_hang=%s',[customer_id])
        if not cursor.fetchone():
            raise HTTPException(404,'Customer not found.')
        lock_stock(cursor,[(warehouse_id,d['product_id']) for d in details])
        cursor.execute("INSERT INTO don_hang (ma_don_hang,ma_nhan_vien,ma_khach_hang,ma_cua_hang,ma_kho,ngay_tao_don,trang_thai) VALUES (%s,%s,%s,%s,%s,%s,'completed')", [order_id,actor['ma_nhan_vien'],customer_id,store_id,warehouse_id,datetime.now(VIETNAM).replace(tzinfo=None)])
        for detail in details:
            sku,quantity=detail['product_id'],detail['quantity']
            cursor.execute('SELECT gia_san_pham FROM san_pham WHERE ma_san_pham=%s FOR SHARE',[sku])
            price=cursor.fetchone()['gia_san_pham']
            discount=detail.get('discount',0)
            if discount>quantity*price:
                raise HTTPException(422,'Discount exceeds line amount.')
            cursor.execute('INSERT INTO chi_tiet_don_hang (ma_don_hang,ma_san_pham,so_luong,don_gia_ban,giam_gia) VALUES (%s,%s,%s,%s,%s)', [order_id,sku,quantity,price,discount])
            change_stock(cursor,actor,warehouse_id,sku,-quantity,'sale','Sale',order=order_id)
    return order_id


def list_orders(actor,permission='sales.read',limit=100,offset=0):
    condition,params=store_scope(actor,permission=permission)
    return rows(f"""SELECT d.*,ch.ten_cua_hang,
        COALESCE(SUM(ct.so_luong*ct.don_gia_ban-ct.giam_gia),0) AS total,
        COALESCE(SUM(ct.so_luong),0) AS quantity
        FROM don_hang d LEFT JOIN cua_hang ch ON ch.ma_cua_hang=d.ma_cua_hang
        LEFT JOIN chi_tiet_don_hang ct ON ct.ma_don_hang=d.ma_don_hang
        WHERE {condition} GROUP BY d.ma_don_hang,ch.ten_cua_hang
        ORDER BY d.ngay_tao_don DESC,d.ma_don_hang DESC LIMIT %s OFFSET %s""",[*params,limit,offset])


def get_order(actor,order_id,permission='sales.read'):
    with transaction() as cursor:
        condition,params=store_scope(actor,permission=permission)
        cursor.execute(f'SELECT d.* FROM don_hang d LEFT JOIN cua_hang ch ON ch.ma_cua_hang=d.ma_cua_hang WHERE d.ma_don_hang=%s AND {condition}',[order_id,*params])
        header=cursor.fetchone()
        if not header:
            raise HTTPException(404,'Order not found in scope.')
        cursor.execute('SELECT * FROM chi_tiet_don_hang WHERE ma_don_hang=%s ORDER BY ma_san_pham',[order_id])
        header['details']=cursor.fetchall()
        return header


def cancel_order(actor,order_id):
    with transaction() as cursor:
        condition,params=store_scope(actor,permission='sales.cancel')
        cursor.execute(f'SELECT d.* FROM don_hang d LEFT JOIN cua_hang ch ON ch.ma_cua_hang=d.ma_cua_hang WHERE d.ma_don_hang=%s AND {condition} FOR UPDATE',[order_id,*params])
        header=cursor.fetchone()
        if not header:
            raise HTTPException(404,'Order not found in scope.')
        if header['trang_thai']=='cancelled':
            return {'status':'cancelled'}
        if header['trang_thai']!='completed':
            raise HTTPException(409,'Legacy order needs review; stock was never booked.')
        cursor.execute('SELECT ma_san_pham,so_luong FROM chi_tiet_don_hang WHERE ma_don_hang=%s',[order_id])
        details=cursor.fetchall()
        # Reversals must also work for subsequently deactivated SKUs.
        for line in sorted(details,key=lambda d:d['ma_san_pham']):
            cursor.execute('SELECT so_luong FROM ton_kho WHERE ma_kho=%s AND ma_san_pham=%s FOR UPDATE',[header['ma_kho'],line['ma_san_pham']])
            if cursor.fetchone() is None:
                raise HTTPException(409,'Stock history missing.')
        for line in details:
            change_stock(cursor,actor,header['ma_kho'],line['ma_san_pham'],line['so_luong'],'cancel_sale','Cancel sale',order=order_id)
        cursor.execute("UPDATE don_hang SET trang_thai='cancelled' WHERE ma_don_hang=%s",[order_id])
    return {'status':'cancelled'}

"""Read-only document helpers backed by scoped services."""
from fastapi import HTTPException
from app.db.helpers import rows
from app.permissions import warehouse_scope,require_permission
from app.repositories.orders import list_orders,get_order,cancel_order


def document_scope(kind,actor):
    from app.permissions import store_scope
    return store_scope(actor,permission='sales.read' if kind=='orders' else 'inventory.read')


def document_base(kind):
    if kind=='orders':
        return 'FROM don_hang d LEFT JOIN cua_hang ch ON ch.ma_cua_hang=d.ma_cua_hang','ma_don_hang','chi_tiet_don_hang','ngay_tao_don'
    return 'FROM phan_phoi d LEFT JOIN cua_hang ch ON ch.ma_cua_hang=d.ma_cua_hang','ma_phan_phoi','chi_tiet_phan_phoi','ngay_phan_phoi'


def list_documents(kind,actor,search='',limit=100,offset=0,**filters):
    if kind=='orders':
        require_permission(actor,'sales.read')
        return {'items':list_orders(actor,limit=limit,offset=offset)}
    require_permission(actor,'inventory.read')
    source,sp=warehouse_scope(actor,'src')
    target,tp=warehouse_scope(actor,'dst')
    return {'items':rows(f'SELECT d.* FROM phan_phoi d LEFT JOIN kho src ON src.ma_kho=d.ma_kho_nguon LEFT JOIN kho dst ON dst.ma_kho=d.ma_kho_dich WHERE {source} OR {target} ORDER BY d.ngay_phan_phoi DESC LIMIT %s OFFSET %s',[*sp,*tp,limit,offset])}


def get_document(kind,actor,record_id):
    if kind=='orders':
        require_permission(actor,'sales.read')
        return get_order(actor,record_id)
    raise HTTPException(410,'Use inventory transfer endpoints.')


def save_document(kind,actor,data,record_id=None):
    raise HTTPException(410,'Use the SKU sales/transfer APIs; saved transactions are immutable.')


def delete_document(kind,actor,record_id):
    if kind=='orders':
        require_permission(actor,'sales.cancel')
        return cancel_order(actor,record_id)
    from app.repositories.inventory import cancel_transfer
    require_permission(actor,'inventory.transfer')
    return cancel_transfer(actor,record_id)

import csv
import io
from fastapi import APIRouter,Depends,Query
from fastapi.responses import Response
from app.core.authentication import require_permissions
from app.repositories.orders import create_order,list_orders,get_order,cancel_order
from app.schemas.orders import OrderInput

router=APIRouter(prefix='/api/orders',tags=['orders'])


@router.post('',status_code=201)
def create_order_endpoint(payload: OrderInput,actor=Depends(require_permissions('sales.create'))):
    code=create_order(actor,payload.customer_id,[d.model_dump() for d in payload.details],payload.store_id,payload.warehouse_id)
    return {'order_id':code,'status':'created'}


@router.get('')
def orders(limit: int=Query(100,ge=1,le=500),offset: int=Query(0,ge=0),actor=Depends(require_permissions('sales.read'))):
    return {'items':list_orders(actor,limit=limit,offset=offset)}


@router.get('/export')
def export_orders(actor=Depends(require_permissions('reports.read'))):
    data=list_orders(actor,permission='reports.read',limit=500)
    output=io.StringIO()
    writer=csv.writer(output)
    writer.writerow(['order_id','store_id','status','total'])
    for row in data:
        # Prefix text values to prevent spreadsheet formula execution.
        writer.writerow(["'"+row['ma_don_hang'],"'"+(row['ma_cua_hang'] or ''),row['trang_thai'],row['total']])
    return Response(output.getvalue(),media_type='text/csv',headers={'Content-Disposition':'attachment; filename=orders.csv','X-Export-Limit':'500'})


@router.get('/{order_id}')
def detail(order_id: str,actor=Depends(require_permissions('sales.read'))):
    return get_order(actor,order_id)


@router.post('/{order_id}/cancel')
def cancel(order_id: str,actor=Depends(require_permissions('sales.cancel'))):
    return cancel_order(actor,order_id)

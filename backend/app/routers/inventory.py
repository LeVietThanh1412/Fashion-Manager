from fastapi import APIRouter, Depends
from pydantic import BaseModel,Field,model_validator
from app.core.authentication import require_permissions
from app.repositories.inventory import (list_inventory,list_warehouses,movements,adjust_stock,transfer_stock,cancel_transfer)
from app.schemas.orders import OrderDetailInput

router=APIRouter(prefix='/api',tags=['inventory'])


class Adjustment(BaseModel):
    warehouse_id: str=Field(min_length=1,max_length=20)
    product_id: str=Field(min_length=1,max_length=20)
    quantity: int=Field(strict=True,ge=-2147483647,le=2147483647)
    reason: str=Field(min_length=1,max_length=255)

    @model_validator(mode='after')
    def nonzero(self):
        if not self.quantity:
            raise ValueError('Adjustment cannot be zero.')
        return self


class Transfer(BaseModel):
    source_id: str=Field(min_length=1,max_length=20)
    target_id: str=Field(min_length=1,max_length=20)
    details: list[OrderDetailInput]=Field(min_length=1,max_length=200)

    @model_validator(mode='after')
    def unique(self):
        if len({d.product_id for d in self.details})!=len(self.details):
            raise ValueError('Duplicate SKU.')
        return self


@router.get('/warehouses')
def warehouses(actor=Depends(require_permissions('inventory.read'))):
    return {'items':list_warehouses(actor)}


@router.get('/inventory')
def inventory(actor=Depends(require_permissions('inventory.read'))):
    return {'items':list_inventory(actor)}


@router.get('/inventory/movements')
def history(actor=Depends(require_permissions('inventory.read'))):
    return {'items':movements(actor)}


@router.post('/inventory/adjustments',status_code=201)
def adjust(payload: Adjustment,actor=Depends(require_permissions('inventory.adjust'))):
    return adjust_stock(actor,payload.warehouse_id,payload.product_id,payload.quantity,payload.reason)


@router.post('/inventory/transfers',status_code=201)
def transfer(payload: Transfer,actor=Depends(require_permissions('inventory.transfer'))):
    return transfer_stock(actor,payload.source_id,payload.target_id,[d.model_dump() for d in payload.details])


@router.post('/inventory/transfers/{transfer_id}/cancel')
def cancel(transfer_id: str,actor=Depends(require_permissions('inventory.transfer'))):
    return cancel_transfer(actor,transfer_id)

from datetime import date
from typing import Literal
from fastapi import APIRouter,Depends,HTTPException
from app.core.authentication import require_permissions
from app.reports import business_report

router=APIRouter(prefix='/api/reports',tags=['reports'])


@router.get('')
def report(start: date,end: date,group: Literal['day','month','store','employee','region']='store',actor=Depends(require_permissions('reports.read'))):
    if end<start:
        raise HTTPException(422,'End date must follow start date.')
    return business_report(actor,start,end,group)

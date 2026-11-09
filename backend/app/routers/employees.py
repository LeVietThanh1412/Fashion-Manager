from fastapi import APIRouter, Depends
from app.core.authentication import require_permissions
from app.repositories.employees import (create_employee,delete_employee,get_distribution,
    list_employees,list_stores,set_employee_status,update_salary,transfer_work)
from app.schemas.employees import EmployeeInput,SalaryInput,StatusInput,WorkInput
from app.db.helpers import rows

router = APIRouter(prefix='/api',tags=['employees'])


@router.get('/positions')
def positions(actor=Depends(require_permissions('employees.write'))):
    return {'items':rows('SELECT * FROM chuc_vu ORDER BY ten_chuc_vu')}


@router.get('/employees')
def employees(actor=Depends(require_permissions('employees.read'))):
    return {'items':list_employees(actor),'capabilities':{'status_management':True}}


@router.get('/employees/stores')
def employee_stores(actor=Depends(require_permissions('employees.write'))):
    return {'items':list_stores(actor)}


@router.post('/employees',status_code=201)
def add_employee(payload: EmployeeInput,actor=Depends(require_permissions('employees.write'))):
    create_employee(payload.model_dump(),actor)
    return {'employee_id':payload.employee_id,'status':'created','login_created':False}


@router.put('/employees/{employee_id}/salary')
def change_salary(employee_id: str,payload: SalaryInput,actor=Depends(require_permissions('employees.salary'))):
    update_salary(employee_id,payload.salary,actor)
    return {'employee_id':employee_id,'status':'salary_updated'}


@router.delete('/employees/{employee_id}')
def dismiss_employee(employee_id: str,actor=Depends(require_permissions('employees.write'))):
    delete_employee(employee_id,actor)
    return {'employee_id':employee_id,'status':'inactive'}


@router.put('/employees/{employee_id}/status')
def change_employee_status(employee_id: str,payload: StatusInput,actor=Depends(require_permissions('employees.write'))):
    set_employee_status(employee_id,payload.status,actor)
    return {'employee_id':employee_id,'status':payload.status}


@router.post('/employees/{employee_id}/work')
def work(employee_id: str,payload: WorkInput,actor=Depends(require_permissions('employees.write'))):
    return transfer_work(employee_id,payload.store_id,actor)


@router.get('/employee/distribution')
def own_store_distribution(actor=Depends(require_permissions('inventory.read'))):
    return {'items':get_distribution(actor),'quantity_type':'on_hand'}

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.authentication import require_roles
from app.repositories.employees import (
    create_employee,
    demote_role,
    get_distribution,
    get_employee,
    list_employees,
    list_stores,
    set_employee_status,
    store_region,
    update_salary,
)
from app.schemas.employees import EmployeeInput, RoleDemotionInput, SalaryInput, StatusInput

router = APIRouter(prefix="/api", tags=["employees"])
MANAGEMENT_ROLES = ("admin", "regional_manager", "store_manager")


def can_manage(actor: dict[str, Any], target: dict[str, Any]) -> bool:
    if actor["ma_nhan_vien"] == target["ma_nhan_vien"] or target["quyen_han"] == "admin":
        return False
    if actor["quyen_han"] == "admin":
        return True
    if actor["quyen_han"] == "regional_manager":
        return (
            target["quyen_han"] in {"store_manager", "staff"}
            and target["store_region"] == actor["khu_vuc_quan_ly"]
        )
    return (
        actor["quyen_han"] == "store_manager"
        and target["quyen_han"] == "staff"
        and target["ma_cua_hang"] == actor["ma_cua_hang"]
    )


@router.get("/employees")
def employees(actor: dict[str, Any] = Depends(require_roles(*MANAGEMENT_ROLES))) -> dict[str, Any]:
    return {
        "items": list_employees(actor),
        "capabilities": {"status_management": False},
    }


@router.get("/employees/stores")
def employee_stores(actor: dict[str, Any] = Depends(require_roles(*MANAGEMENT_ROLES))) -> dict[str, Any]:
    return {"items": list_stores(actor)}


@router.post("/employees", status_code=status.HTTP_201_CREATED)
def add_employee(
    payload: EmployeeInput,
    actor: dict[str, Any] = Depends(require_roles(*MANAGEMENT_ROLES)),
) -> dict[str, str]:
    role = actor["quyen_han"]
    if payload.role == "admin":
        raise HTTPException(status_code=403, detail="Không thể tạo tài khoản admin qua API.")
    if role == "store_manager" and payload.role != "staff":
        raise HTTPException(status_code=403, detail="Quản lý cửa hàng chỉ được thêm nhân viên.")
    if role == "regional_manager" and payload.role not in {"store_manager", "staff"}:
        raise HTTPException(status_code=403, detail="Quản lý khu vực chỉ được thêm quản lý cửa hàng hoặc nhân viên.")

    if payload.role == "regional_manager":
        if role != "admin" or payload.region_id is None or payload.store_id is not None:
            raise HTTPException(status_code=403, detail="Chỉ admin được tạo quản lý khu vực và phải chỉ định khu vực.")
    else:
        if not payload.store_id or payload.region_id is not None:
            raise HTTPException(status_code=422, detail="Nhân viên và quản lý cửa hàng phải được gán cửa hàng.")
        region_id = store_region(payload.store_id)
        if region_id is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy cửa hàng.")
        if role == "regional_manager" and region_id != actor["khu_vuc_quan_ly"]:
            raise HTTPException(status_code=403, detail="Cửa hàng nằm ngoài khu vực được phân công.")
        if role == "store_manager" and payload.store_id != actor["ma_cua_hang"]:
            raise HTTPException(status_code=403, detail="Chỉ được thêm nhân viên vào cửa hàng của bạn.")

    if payload.salary is None:
        raise HTTPException(status_code=422, detail="Lương là bắt buộc và phải lớn hơn 0 theo ràng buộc database.")

    create_employee(
        {
            "employee_id": payload.employee_id,
            "name": payload.name,
            "phone": payload.phone,
            "email": payload.email,
            "store_id": payload.store_id,
            "role": payload.role,
            "region_id": payload.region_id,
            "salary": payload.salary,
        },
        actor["ma_nhan_vien"],
    )
    return {"employee_id": payload.employee_id, "status": "created"}


@router.put("/employees/{employee_id}/salary")
def change_salary(
    employee_id: str,
    payload: SalaryInput,
    actor: dict[str, Any] = Depends(require_roles(*MANAGEMENT_ROLES)),
) -> dict[str, str]:
    target = get_employee(employee_id)
    if not target:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên.")
    if not can_manage(actor, target):
        raise HTTPException(status_code=403, detail="Bạn không được thay đổi lương của nhân viên này.")
    if not update_salary(employee_id, payload.salary, actor):
        raise HTTPException(status_code=409, detail="Không thể cập nhật lương; hãy tải lại danh sách.")
    return {"employee_id": employee_id, "status": "salary_updated"}


@router.post("/employees/{employee_id}/demote")
def demote_employee_role(
    employee_id: str,
    payload: RoleDemotionInput,
    actor: dict[str, Any] = Depends(require_roles("admin", "regional_manager")),
) -> dict[str, str]:
    target = get_employee(employee_id)
    if not target:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên.")
    if target["quyen_han"] not in {"regional_manager", "store_manager"} or not can_manage(actor, target):
        raise HTTPException(status_code=403, detail="Không thể hạ quyền vai trò này.")
    store_id = target["ma_cua_hang"]
    if target["quyen_han"] == "regional_manager":
        if actor["quyen_han"] != "admin":
            raise HTTPException(status_code=403, detail="Chỉ admin được hạ quyền quản lý khu vực.")
        if not payload.store_id or store_region(payload.store_id) != target["khu_vuc_quan_ly"]:
            raise HTTPException(status_code=422, detail="Hãy chọn cửa hàng thuộc khu vực quản lý hiện tại.")
        store_id = payload.store_id
    if not demote_role(employee_id, store_id, actor):
        raise HTTPException(status_code=409, detail="Không thể hạ quyền; hãy tải lại danh sách.")
    return {"employee_id": employee_id, "status": "role_demoted"}


@router.put("/employees/{employee_id}/status")
def change_employee_status(
    employee_id: str,
    payload: StatusInput,
    actor: dict[str, Any] = Depends(require_roles(*MANAGEMENT_ROLES)),
) -> dict[str, str]:
    target = get_employee(employee_id)
    if not target:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên.")
    if not can_manage(actor, target):
        raise HTTPException(status_code=403, detail="Bạn không được thay đổi trạng thái nhân viên này.")
    if payload.status == "active" and actor["quyen_han"] != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin được kích hoạt lại tài khoản.")
    if not set_employee_status(employee_id, payload.status, actor):
        raise HTTPException(
            status_code=409,
            detail="Schema database hiện tại không có cột trạng thái nhân viên.",
        )
    return {"employee_id": employee_id, "status": payload.status}


@router.get("/employee/distribution")
def own_store_distribution(
    actor: dict[str, Any] = Depends(require_roles("staff")),
) -> dict[str, Any]:
    if not actor["ma_cua_hang"]:
        raise HTTPException(status_code=409, detail="Tài khoản chưa được gán cửa hàng.")
    return {"items": get_distribution(actor["ma_cua_hang"]), "quantity_type": "distributed"}

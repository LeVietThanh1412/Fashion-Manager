from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.authentication import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.core.phone import normalize_phone
from app.db.helpers import transaction
from app.repositories.auth import get_user_by_phone

router = APIRouter(prefix="/api/auth", tags=["authentication"])


class LoginInput(BaseModel):
    phone: str = Field(min_length=1, max_length=25)
    password: str = Field(min_length=1, max_length=128)


class PasswordChangeInput(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=12, max_length=128)


def public_user(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "employee_id": user["ma_nhan_vien"],
        "name": user["ho_ten"],
        "phone": user["so_dien_thoai"],
        "email": user.get("email"),
        "manager_id": user.get("ma_quan_ly"),
        "salary": user.get("luong"),
        "role": user["quyen_han"],
        "region_id": user["khu_vuc_quan_ly"],
        "store_id": user["ma_cua_hang"],
        "store_region": user["store_region"],
        "account_id": user["ma_tai_khoan"],
        "assignments": user["assignments"],
        "workplaces": user.get("workplaces", []),
        "permissions": sorted({p for g in user["assignments"] for p in g["permissions"]}),
    }


@router.post("/password")
def change_password(
    payload: PasswordChangeInput,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    with transaction() as cursor:
        cursor.execute(
            """SELECT tk.mat_khau_hash,tk.auth_version
            FROM tai_khoan tk JOIN nhan_vien nv ON nv.ma_nhan_vien=tk.ma_nhan_vien
            WHERE tk.ma_tai_khoan=%s AND tk.trang_thai='active' AND nv.trang_thai='active'
            FOR UPDATE""",
            [user["ma_tai_khoan"]],
        )
        account = cursor.fetchone()
        if not account or not verify_password(payload.current_password, account["mat_khau_hash"]):
            raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không đúng.")
        if verify_password(payload.new_password, account["mat_khau_hash"]):
            raise HTTPException(status_code=422, detail="Mật khẩu mới phải khác mật khẩu hiện tại.")
        cursor.execute(
            """UPDATE tai_khoan SET mat_khau_hash=%s,auth_version=auth_version+1
            WHERE ma_tai_khoan=%s""",
            [hash_password(payload.new_password), user["ma_tai_khoan"]],
        )
        auth_version = account["auth_version"] + 1

    token, expires_in = create_access_token(user["ma_tai_khoan"], auth_version)
    return {"access_token": token, "token_type": "bearer", "expires_in": expires_in}


@router.post("/login")
def login(payload: LoginInput) -> dict[str, Any]:
    try:
        phone = normalize_phone(payload.phone)
    except ValueError:
        phone = ''
    user = get_user_by_phone(phone) if phone else None
    if not user or user["trang_thai"] != "active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Số điện thoại hoặc mật khẩu không đúng.")

    password_valid = verify_password(payload.password, user.get("mat_khau_hash"))
    if not password_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Số điện thoại hoặc mật khẩu không đúng.")

    token, expires_in = create_access_token(user["ma_tai_khoan"],user['auth_version'])
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": public_user(user),
    }


@router.get("/me")
def me(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    return {"user": public_user(user)}

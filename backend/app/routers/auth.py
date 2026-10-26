from typing import Any
import hmac

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.authentication import get_current_user
from app.core.security import create_access_token
from app.repositories.auth import get_user_by_phone

router = APIRouter(prefix="/api/auth", tags=["authentication"])


class LoginInput(BaseModel):
    phone: str = Field(min_length=1, max_length=25)
    password: str = Field(min_length=1, max_length=128)


def public_user(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "employee_id": user["ma_nhan_vien"],
        "name": user["ho_ten"],
        "phone": user["so_dien_thoai"],
        "role": user["quyen_han"],
        "region_id": user["khu_vuc_quan_ly"],
        "store_id": user["ma_cua_hang"],
        "store_region": user["store_region"],
    }


@router.post("/login")
def login(payload: LoginInput) -> dict[str, Any]:
    user = get_user_by_phone(payload.phone.strip())
    if not user or user["trang_thai"] != "active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Số điện thoại hoặc mật khẩu không đúng.")

    password_valid = hmac.compare_digest(
        payload.password.encode("utf-8"),
        user["ma_nhan_vien"].encode("utf-8"),
    )
    if not password_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Số điện thoại hoặc mật khẩu không đúng.")

    token, expires_in = create_access_token(user["ma_nhan_vien"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": public_user(user),
    }


@router.get("/me")
def me(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    return {"user": public_user(user)}

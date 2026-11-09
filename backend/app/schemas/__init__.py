"""Dữ liệu của các form. Tên trường giữ giống các bảng SQL để dễ đối chiếu."""
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Code = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
Phone = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=25)]
Money = Annotated[Decimal, Field(ge=0, max_digits=15, decimal_places=2)]


class Form(BaseModel):
    model_config = ConfigDict(extra='forbid')


class Category(Form):
    ma_danh_muc: Code
    ten_danh_muc: Name


class Product(Form):
    ma_san_pham: Code
    ma_mau: Code
    mau_sac: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
    kich_co: Code
    gia_san_pham: Money


class Store(Form):
    ma_cua_hang: Code
    ten_cua_hang: Name
    khu_vuc: int = Field(ge=1)
    dia_chi: Name
    so_dien_thoai: Phone
    email: Name


class Assignment(Form):
    pham_vi: Literal['system','region','store','warehouse']
    ma_khu_vuc: int | None = None
    ma_cua_hang: Code | None = None
    ma_kho: Code | None = None

    @model_validator(mode='after')
    def valid_scope(self):
        key={'system':None,'region':'ma_khu_vuc','store':'ma_cua_hang','warehouse':'ma_kho'}[self.pham_vi]
        if any((getattr(self,k) is not None)!=(k==key) for k in ('ma_khu_vuc','ma_cua_hang','ma_kho')):
            raise ValueError('Scope must reference exactly one entity.')
        return self


from app.schemas.employees import EmployeeInput as Employee


class Customer(Form):
    ma_khach_hang: Code
    ho_ten: Name
    so_dien_thoai: Phone


class Line(Form):
    ma_san_pham: Code
    so_luong: int = Field(strict=True, gt=0, le=2147483647)


class OrderLine(Line):
    don_gia_ban: Money | None = None


class Order(Form):
    ma_don_hang: Code
    ma_nhan_vien: Code
    ma_khach_hang: Code
    ngay_tao_don: datetime
    chi_tiet: list[OrderLine] = Field(min_length=1, max_length=200)

    @model_validator(mode='after')
    def unique_products(self):
        validate_lines(self.chi_tiet)
        return self


class Distribution(Form):
    ma_phan_phoi: Code
    ma_cua_hang: Code
    ma_nhan_vien: Code
    ngay_phan_phoi: date
    chi_tiet: list[Line] = Field(min_length=1, max_length=200)

    @model_validator(mode='after')
    def unique_products(self):
        validate_lines(self.chi_tiet)
        return self


def validate_lines(lines):
    if len({line.ma_san_pham for line in lines}) != len(lines):
        raise ValueError('Một sản phẩm chỉ xuất hiện một lần trên phiếu. Hãy cập nhật số lượng.')


class Login(Form):
    ma_nhan_vien: Code

"""Dữ liệu của các form. Tên trường giữ giống các bảng SQL để dễ đối chiếu."""
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Code = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
Phone = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=25)]
Money = Annotated[Decimal, Field(ge=0, max_digits=15, decimal_places=0)]
Role = Literal['admin', 'regional_manager', 'store_manager', 'staff']


class Form(BaseModel):
    model_config = ConfigDict(extra='forbid')


class Category(Form):
    ma_danh_muc: Code
    ten_danh_muc: Name


class Product(Form):
    ma_san_pham: Code
    ma_danh_muc: Code
    ten_san_pham: Name
    mau_sac: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
    kich_co: Code
    gia_san_pham: Money


class Store(Form):
    ma_cua_hang: Code
    ten_cua_hang: Name
    khu_vuc: int = Field(ge=1, le=3)
    dia_chi: Name
    so_dien_thoai: Phone
    email: Name


class Assignment(Form):
    quyen_han: Role
    ma_cua_hang: Code | None = None
    khu_vuc_quan_ly: int | None = Field(default=None, ge=1, le=3)
    ma_quan_ly: Code | None = None
    trang_thai: Literal['active', 'inactive'] = 'active'

    @model_validator(mode='after')
    def scope_matches_role(self):
        if self.quyen_han == 'admin':
            valid = self.ma_cua_hang is None and self.khu_vuc_quan_ly is None
        elif self.quyen_han == 'regional_manager':
            valid = self.ma_cua_hang is None and self.khu_vuc_quan_ly is not None
        else:
            valid = self.ma_cua_hang is not None and self.khu_vuc_quan_ly is None
        if not valid:
            raise ValueError('Vai trò và phạm vi cửa hàng/khu vực không phù hợp.')
        return self


class Employee(Assignment):
    ma_nhan_vien: Code
    ho_ten: Name
    so_dien_thoai: Phone
    email: Name
    luong: Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)] = Decimal(0)
    cap_bac: int = Field(default=2, ge=1, le=3)


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

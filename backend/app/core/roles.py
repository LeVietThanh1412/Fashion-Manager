DATABASE_ROLES = {
    "admin": "quan_ly",
    "regional_manager": "quan_ly_khu_vuc",
    "store_manager": "quan_ly_cua_hang",
    "staff": "nhan_vien",
}
APPLICATION_ROLES = {database_role: role for role, database_role in DATABASE_ROLES.items()}


def role_from_database(value: str) -> str:
    try:
        return APPLICATION_ROLES[value]
    except KeyError as exc:
        raise ValueError(f"Vai trò không được hỗ trợ trong database: {value}") from exc


def role_to_database(value: str) -> str:
    try:
        return DATABASE_ROLES[value]
    except KeyError as exc:
        raise ValueError(f"Vai trò không được hỗ trợ trong ứng dụng: {value}") from exc

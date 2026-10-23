import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    db_host: str = os.getenv("DB_HOST", "127.0.0.1")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_name: str = os.getenv("DB_NAME", "quan_ly_chuoi_thoi_trang")
    db_user: str = os.getenv("DB_USER", "demo_user")
    db_password: str = os.getenv("DB_PASSWORD", "")


settings = Settings()

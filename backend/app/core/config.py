import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    db_host: str = os.getenv("DB_HOST", "127.0.0.1")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_name: str = os.getenv("DB_NAME", "quan_ly_chuoi_thoi_trang")
    db_user: str = os.getenv("DB_USER", "demo_user")
    db_password: str = os.getenv("DB_PASSWORD", "")
    app_cors_origins: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "app_cors_origins",
            [origin.strip() for origin in os.getenv("APP_CORS_ORIGINS", "http://localhost:5173").split(",") if origin.strip()],
        )


settings = Settings()

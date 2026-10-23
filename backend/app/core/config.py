import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


def database_address() -> tuple[str, int]:
    raw = os.getenv("DB_HOST", "127.0.0.1").strip().strip("\"'").strip()
    parsed = urlsplit(raw if "://" in raw else "//" + raw)
    if parsed.scheme and parsed.scheme != "mysql":
        raise ValueError("DB_HOST must be the Aiven hostname or a mysql:// URI.")
    if not parsed.hostname or any(char.isspace() for char in parsed.hostname):
        raise ValueError("DB_HOST is invalid. Copy Host from Aiven Service Overview.")
    port = os.getenv("DB_PORT", "").strip().strip("\"'")
    port_number = int(port) if port else (parsed.port or 3306)
    if not 1 <= port_number <= 65535:
        raise ValueError("DB_PORT must be between 1 and 65535.")
    return parsed.hostname, port_number


DB_HOST, DB_PORT = database_address()


@dataclass(frozen=True)
class Settings:
    db_host: str = DB_HOST
    db_port: int = DB_PORT
    db_name: str = os.getenv("DB_NAME", "quan_ly_chuoi_thoi_trang")
    db_user: str = os.getenv("DB_USER", "demo_user")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_ssl_ca: str = os.getenv("DB_SSL_CA", "").strip()
    app_cors_origins: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "app_cors_origins",
            [origin.strip().rstrip('/') for origin in os.getenv("APP_CORS_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080,http://localhost:5173,http://127.0.0.1:5173").split(",") if origin.strip()],
        )


settings = Settings()

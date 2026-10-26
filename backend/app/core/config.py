import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DOTENV_PATH = PROJECT_ROOT / ".env"
# Existing local setups in this project used the legacy file name `env`.
# Prefer the documented `.env`, but keep that setup working without copying
# credentials or changing the database configuration file.
if not DOTENV_PATH.is_file():
    DOTENV_PATH = PROJECT_ROOT / "env"
load_dotenv(DOTENV_PATH)


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

# Keep the known public site and the local static-server origins available even
# when Render supplies a narrower APP_CORS_ORIGINS value.  The latter previously
# replaced this list entirely, which made the documented Live Server workflow
# fail its CORS preflight request.
DEFAULT_CORS_ORIGINS = (
    "https://thanhtech.cloud",
    "https://levietthanh1412.github.io",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)


def cors_origins() -> list[str]:
    configured = os.getenv("APP_CORS_ORIGINS", "").split(",")
    origins: list[str] = []
    for origin in (*DEFAULT_CORS_ORIGINS, *configured):
        normalized = origin.strip().rstrip("/")
        if normalized and normalized not in origins:
            origins.append(normalized)
    return origins


@dataclass(frozen=True)
class Settings:
    db_host: str = DB_HOST
    db_port: int = DB_PORT
    db_name: str = os.getenv("DB_NAME", "quan_ly_chuoi_thoi_trang")
    db_user: str = os.getenv("DB_USER", "demo_user")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_ssl_ca: str = os.getenv("DB_SSL_CA", "").strip()
    auth_token_secret: str = os.getenv("AUTH_TOKEN_SECRET", "")
    app_cors_origins: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        object.__setattr__(self, "app_cors_origins", cors_origins())


settings = Settings()

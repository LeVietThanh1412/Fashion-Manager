from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import mysql.connector

from app.core.config import settings
from app.db.query_loader import QueryLoader

SQL_ROOT = Path(__file__).resolve().parents[3] / "sql" / "app"
loader = QueryLoader(SQL_ROOT)


@contextmanager
def connection() -> Iterator[Any]:
    tls_options: dict[str, Any] = {}
    if settings.db_ssl_ca:
        tls_options = {
            "ssl_ca": settings.db_ssl_ca,
            "ssl_verify_cert": True,
            "ssl_verify_identity": True,
        }
    conn = mysql.connector.connect(
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        connection_timeout=10,
        **tls_options,
    )
    try:
        if settings.db_host not in {"localhost", "127.0.0.1", "::1"}:
            cursor = conn.cursor()
            try:
                cursor.execute(loader.load("health/ssl_cipher.sql"))
                cipher = cursor.fetchone()
                if not cipher or not cipher[1]:
                    raise mysql.connector.InterfaceError("Remote MySQL connections require TLS.")
            finally:
                cursor.close()
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

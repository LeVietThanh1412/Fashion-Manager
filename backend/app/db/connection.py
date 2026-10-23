from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import mysql.connector

from app.core.config import settings


@contextmanager
def connection() -> Iterator[Any]:
    conn = mysql.connector.connect(
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

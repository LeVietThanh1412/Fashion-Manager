from contextlib import contextmanager

from fastapi import HTTPException

from app.db.connection import connection


@contextmanager
def transaction():
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            yield cursor
            conn.commit()
        finally:
            cursor.close()


def rows(sql, params=()):
    with transaction() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchall()


def one(sql, params=()):
    result = rows(sql, params)
    if not result:
        raise HTTPException(404, 'Không tìm thấy dữ liệu.')
    return result[0]

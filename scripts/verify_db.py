"""Read-only DNS/database/schema check using the same settings and TLS as the API."""
import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))

from app.core.config import settings
from app.db.connection import connection

TABLES = (
    'schema_version','khu_vuc','cua_hang','kho','nhan_vien','tai_khoan','vai_tro','quyen',
    'vai_tro_quyen','phan_cong_quyen','phan_cong_lam_viec','chuc_vu','mau_san_pham','san_pham',
    'ton_kho','bien_dong_kho','don_hang','chi_tiet_don_hang',
)



def main() -> int:
    try:
        socket.getaddrinfo(settings.db_host, settings.db_port, type=socket.SOCK_STREAM)
    except socket.gaierror:
        print('FAIL: DB_HOST cannot be resolved by DNS. Copy the Host field from Aiven Service Overview; check for typos or a deleted/paused service. Do not use a service name or connection URI as the hostname.')
        return 1
    print('PASS: DB_HOST resolves in DNS')
    try:
        with connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT VERSION()')
                print(f'MySQL version: {cursor.fetchone()[0]}')
                for table in TABLES:
                    cursor.execute(f'SELECT COUNT(*) FROM `{table}`')
                    print(f'PASS: {table} has {cursor.fetchone()[0]} rows')
                cursor.execute('SELECT version FROM schema_version')
                if cursor.fetchall() != [(3,)]:
                    print('FAIL: backend requires schema v3; initialize a new database first.')
                    return 1
            finally:
                cursor.close()
    except Exception as exc:
        errno = getattr(exc, 'errno', None)
        print(f'FAIL: database verification ({type(exc).__name__}, code={errno}). Check DB credentials, Aiven network access, TLS certificate and schema. No seed data is inserted automatically.')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

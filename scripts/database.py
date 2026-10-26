"""Chạy SQL của project. Mặc định chỉ nâng cấp; --reset tạo mới và xóa dữ liệu cũ."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'backend'))
from app.db.connection import connection


def statements(path):
    """Hỗ trợ DELIMITER của MySQL Workbench, dùng cho procedure minh họa."""
    delimiter = ';'
    buffer = []
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        if line.strip().startswith('--') or not line.strip():
            continue
        if line.strip().upper().startswith('DELIMITER '):
            delimiter = line.strip().split()[1]
            continue
        buffer.append(line)
        if line.rstrip().endswith(delimiter):
            yield '\n'.join(buffer).rstrip()[:-len(delimiter)].strip()
            buffer = []
    if buffer:
        raise ValueError(f'SQL chưa kết thúc: {path}')


def run_file(conn, path, verbose=True):
    cursor = conn.cursor()
    try:
        for sql in statements(path):
            cursor.execute(sql)
            while True:
                if cursor.with_rows:
                    values = cursor.fetchall()
                    if verbose and values:
                        for value in values:
                            print(value)
                if not cursor.nextset():
                    break
        conn.commit()
    finally:
        cursor.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reset', action='store_true', help='Xóa và tạo lại database demo trong file 1, sau đó nạp file 2')
    parser.add_argument('--demo-constraints', action='store_true', help='Chạy file 3, dữ liệu demo được rollback')
    args = parser.parse_args()
    # Cho phép bootstrap khi database chưa tồn tại.
    from app.core.config import settings
    import mysql.connector
    options = dict(host=settings.db_host,port=settings.db_port,user=settings.db_user,password=settings.db_password,connection_timeout=10)
    if settings.db_ssl_ca:
        options.update(ssl_ca=settings.db_ssl_ca,ssl_verify_cert=True,ssl_verify_identity=True)
    conn = mysql.connector.connect(**options)
    try:
        files = ['1.TaoCoSoDuLieu.sql','2.ThemDuLieu.sql'] if args.reset else ['4.CapNhatPhanQuyen.sql']
        if args.demo_constraints:
            files.append('3.UpdateDeleteRangBuoc.sql')
        for name in files:
            print('Running',name)
            run_file(conn,ROOT/'sql'/name)
    finally:
        conn.close()


if __name__ == '__main__':
    main()

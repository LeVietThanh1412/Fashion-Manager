"""Fresh versioned database lifecycle for explicitly named local development databases."""
import argparse
import getpass
import hashlib
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
VERSION = 3
CREATE_SQL = ROOT/'sql/data/01_create_database.sql'
SEED_SQL = ROOT/'sql/data/02_seed_data.sql'


def statements(path, section=None):
    delimiter = ';'
    buffer = []
    active = section is None
    for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
        marker = re.fullmatch(r'-- @([a-z]+)',line.strip())
        if marker:
            if buffer:
                raise ValueError(f'Section changed inside SQL statement: {path}')
            active = section is None or marker.group(1)==section
            continue
        if not active:
            continue
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
        raise ValueError(f'Unterminated SQL: {path}')


def run_file(conn, path, verbose=True, section=None, database=None):
    cursor = conn.cursor()
    try:
        for sql in statements(path,section):
            if section=='database':
                if not database or not re.fullmatch(r'fashion_(test|dev)_[a-zA-Z0-9_]+',database):
                    raise ValueError('An explicitly validated development/test database name is required.')
                sql=sql.replace('`fashion_dev_local`',f'`{database}`')
            cursor.execute(sql)
            while True:
                if cursor.with_rows:
                    values = cursor.fetchall()
                    if verbose:
                        for value in values:
                            print(value)
                if not cursor.nextset():
                    break
        conn.commit()
    finally:
        cursor.close()


def _section_bytes(path, section):
    content=Path(path).read_bytes().replace(b'\r\n',b'\n')
    marker=f'-- @{section}\n'.encode('ascii')
    start=content.index(marker)+len(marker)
    end=content.find(b'-- @',start)
    return content[start:] if end<0 else content[start:end]


def fingerprint():
    digest = hashlib.sha256()
    # Normalize only creation guards. Existing v3 installations retain their checksum.
    digest.update(_section_bytes(CREATE_SQL,'tables').replace(b'CREATE TABLE IF NOT EXISTS ',b'CREATE TABLE '))
    digest.update(_section_bytes(SEED_SQL,'system'))
    digest.update(_section_bytes(CREATE_SQL,'views').replace(b'CREATE OR REPLACE VIEW ',b'CREATE VIEW '))
    return digest.hexdigest()


def apply(conn, mode):
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT DATABASE()')
        if not cursor.fetchone()[0]:
            raise ValueError('Select the exact target database before installing tables.')
        cursor.execute('SHOW TABLES')
        tables = {row[0] for row in cursor.fetchall()}
        if 'schema_version' in tables:
            cursor.execute('SELECT version,checksum FROM schema_version ORDER BY version')
            versions = cursor.fetchall()
            if versions:
                if versions != [(VERSION, fingerprint())]:
                    raise ValueError('Unknown version or checksum mismatch; create a new migration.')
                print(f'PASS: schema v{VERSION} already installed; no DDL or seed executed.')
                return False
            raise ValueError('Interrupted installation detected. Reset the verified local development database.')
        if mode == 'status':
            print('Unversioned database; no changes made.')
            return False
        if tables:
            raise ValueError('init requires an empty database. Use reset-dev only for a verified local development target.')
        run_file(conn, CREATE_SQL, False, section='tables')
        run_file(conn, SEED_SQL, False, section='system')
        run_file(conn, CREATE_SQL, False, section='views')
        cursor.execute('INSERT INTO schema_version (version,checksum,source) VALUES (%s,%s,%s)',
                       (VERSION, fingerprint(), mode))
        conn.commit()
        print(f'PASS: schema v{VERSION} installed via {mode}.')
        return True
    finally:
        cursor.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('init','reset-dev','status'))
    parser.add_argument('--database', required=True)
    parser.add_argument('--host', choices=('127.0.0.1','localhost','::1'), default='127.0.0.1')
    parser.add_argument('--port', type=int, default=3308)
    parser.add_argument('--user', default='root')
    parser.add_argument('--config', help='Explicit local development env file; required for reset-dev')
    parser.add_argument('--demo', action='store_true', help='Load the demo section of the one data SQL file on fresh init')
    args = parser.parse_args()
    if not re.fullmatch(r'fashion_(test|dev)_[a-zA-Z0-9_]+', args.database):
        parser.error('Only explicitly named fashion_test_* or fashion_dev_* local clones are supported.')
    if args.mode == 'reset-dev':
        if not args.config or not re.fullmatch(r'fashion_dev_[a-zA-Z0-9_]+',args.database):
            parser.error('reset-dev requires --config and an explicit fashion_dev_* database.')
        from dotenv import dotenv_values
        config = dotenv_values(args.config)
        if (config.get('APP_ENV') != 'development' or config.get('DB_NAME') != args.database
                or config.get('DB_HOST') != args.host or str(config.get('DB_PORT')) != str(args.port)
                or config.get('DB_USER') != args.user):
            parser.error('Target host, port, user and database must exactly match a local APP_ENV=development config.')
    import mysql.connector
    password = os.getenv('FASHION_LOCAL_DB_PASSWORD')
    if password is None:
        password = getpass.getpass('Local MySQL password: ')
    conn = mysql.connector.connect(host=args.host,port=args.port,user=args.user,password=password)
    cursor = conn.cursor()
    try:
        cursor.execute("SET time_zone = '+00:00'")
        cursor.execute('SELECT GET_LOCK(%s,0)', ('fashion_lifecycle_'+args.database,))
        if cursor.fetchone()[0] != 1:
            raise ValueError('Another lifecycle operation is in progress.')
        if args.mode == 'reset-dev':
            cursor.execute('SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME=%s',[args.database])
            if not cursor.fetchone():
                raise ValueError('The configured development database does not exist; use init instead.')
            cursor.execute(f'DROP DATABASE `{args.database}`')
        if args.mode == 'status':
            cursor.execute(f'USE `{args.database}`')
        else:
            run_file(conn,CREATE_SQL,False,section='database',database=args.database)
        fresh=apply(conn,'status' if args.mode=='status' else 'init')
        if args.demo and args.mode!='status':
            if not fresh:
                raise ValueError('Demo data can only be installed during a fresh init.')
            run_file(conn, SEED_SQL,False,section='demo')
            print('PASS: demo seed installed.')
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    main()

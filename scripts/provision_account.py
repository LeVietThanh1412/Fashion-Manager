"""Provision a local-clone account with an operator-supplied password, never an employee-code password."""
import argparse
import getpass
import os
from pathlib import Path
import re
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.core.security import hash_password
from scripts.database import VERSION,fingerprint


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',required=True)
    parser.add_argument('--port',type=int,default=3308)
    parser.add_argument('--user',default='root')
    parser.add_argument('--employee',required=True)
    parser.add_argument('--account',required=True)
    parser.add_argument('--bootstrap-admin',action='store_true')
    args=parser.parse_args()
    if not re.fullmatch(r'fashion_(test|dev)_[a-zA-Z0-9_]+',args.database):
        parser.error('Only fashion_test_* or fashion_dev_* local clones are supported.')
    password=getpass.getpass('New account password (12+ characters; input hidden, type then Enter): ')
    if password!=getpass.getpass('Repeat account password (input hidden, type then Enter): '):
        parser.error('Passwords differ.')
    encoded=hash_password(password)
    import mysql.connector
    db_password=os.getenv('FASHION_LOCAL_DB_PASSWORD')
    if db_password is None:
        db_password=getpass.getpass('Local MySQL password: ')
    conn=mysql.connector.connect(host='127.0.0.1',port=args.port,user=args.user,password=db_password,database=args.database)
    cursor=conn.cursor(dictionary=True)
    try:
        cursor.execute("SET time_zone='+00:00'")
        cursor.execute('SELECT version,checksum FROM schema_version')
        if cursor.fetchall()!=[{'version':VERSION,'checksum':fingerprint()}]:
            raise ValueError('Install the current schema baseline first.')
        cursor.execute('SELECT GET_LOCK(%s,0)',('fashion_bootstrap_'+args.database,))
        if next(iter(cursor.fetchone().values()))!=1:
            raise ValueError('Another account provisioning operation is running.')
        cursor.execute("SELECT ma_nhan_vien FROM nhan_vien WHERE ma_nhan_vien=%s AND trang_thai='active'",[args.employee])
        if not cursor.fetchone():
            raise ValueError('Create an active personnel profile first.')
        cursor.execute('SELECT * FROM tai_khoan WHERE ma_nhan_vien=%s FOR UPDATE',[args.employee])
        old=cursor.fetchone()
        if old:
            if old['ma_tai_khoan']!=args.account:
                raise ValueError('Employee already has a different account ID.')
            cursor.execute("UPDATE tai_khoan SET mat_khau_hash=%s,trang_thai='active',auth_version=auth_version+1 WHERE ma_tai_khoan=%s",[encoded,args.account])
        else:
            cursor.execute("INSERT INTO tai_khoan (ma_tai_khoan,ma_nhan_vien,mat_khau_hash,trang_thai) VALUES (%s,%s,%s,'active')",[args.account,args.employee,encoded])
        if args.bootstrap_admin:
            cursor.execute("SELECT ma_phan_cong FROM phan_cong_quyen WHERE ma_vai_tro='system_admin' LIMIT 1")
            if cursor.fetchone():
                raise ValueError('An administrator assignment already exists. Use the authorized access API.')
            cursor.execute("INSERT INTO phan_cong_quyen (ma_tai_khoan,ma_vai_tro,pham_vi,duoc_uy_quyen) VALUES (%s,'system_admin','system',TRUE)",[args.account])
        conn.commit()
        print('PASS: account provisioned. No password or token printed.')
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


if __name__=='__main__':
    main()

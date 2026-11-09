"""Real MySQL coverage. Explicit opt-in, local port, unique throwaway databases only."""
import os
import re
import secrets
from contextlib import contextmanager
from dataclasses import replace
from datetime import datetime,timedelta,timezone
from pathlib import Path
from uuid import uuid4

import mysql.connector
import pytest
from fastapi.testclient import TestClient
from app.core.config import settings
from app.core.security import hash_password,verify_password
from app.db.academic_queries import load_academic_queries
from main import app
from scripts.database import apply,run_file,main as database_main
import sys

pytestmark=pytest.mark.skipif(os.getenv('FASHION_TEST_MYSQL')!='1',reason='Opt-in isolated MySQL integration test')
ROOT=Path(__file__).resolve().parents[2]


@pytest.fixture
def local_db():
    port=int(os.getenv('FASHION_TEST_PORT','3308'))
    assert port==3308,'Only the dedicated local test port is supported.'
    options=dict(host='127.0.0.1',port=port,user='root',password=os.getenv('FASHION_LOCAL_DB_PASSWORD',''))
    name='fashion_test_'+uuid4().hex
    conn=mysql.connector.connect(**options)
    cursor=conn.cursor(dictionary=True)
    cursor.execute(f'CREATE DATABASE `{name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci')
    cursor.execute(f'USE `{name}`')
    cursor.execute("SET time_zone='+00:00'")
    yield conn,cursor,options,name
    cursor.close()
    conn.close()
    assert re.fullmatch(r'fashion_test_[0-9a-f]{32}',name)
    cleanup=mysql.connector.connect(**options)
    c=cleanup.cursor()
    c.execute(f'DROP DATABASE `{name}`')
    c.close()
    cleanup.close()


@pytest.fixture
def api(local_db,monkeypatch):
    conn,cursor,options,name=local_db
    apply(conn,'init')
    cursor.execute("INSERT INTO khu_vuc VALUES (99,'Additional region')")
    cursor.execute("INSERT INTO danh_muc VALUES ('SHOE','Test shoes')")
    cursor.execute("INSERT INTO cua_hang VALUES ('S1','Shop 1',1,'A','1001','s1@test','active'),('S2','Shop 2',99,'B','1002','s2@test','active')")
    cursor.execute("INSERT INTO kho VALUES ('K1','Store stock','store','S1',NULL,'active'),('K2','Second stock','store','S2',NULL,'active'),('KC','Central stock','central',NULL,1,'active')")
    cursor.execute("INSERT INTO mau_san_pham VALUES ('M1','SHOE','Shoe model','active')")
    cursor.execute("INSERT INTO san_pham VALUES ('SKU1','M1','Black','39',100.50,'active'),('SKU2','M1','White','40',200,'active')")
    cursor.execute("INSERT INTO khach_hang VALUES ('C1','Customer 1','2001'),('C2','Customer 2','2002')")
    password=secrets.token_urlsafe(24)
    encoded=hash_password(password)
    for index,employee in enumerate(('ADMIN','SELLER','MANAGER','OTHER','MULTI')):
        cursor.execute('INSERT INTO nhan_vien VALUES (%s,%s,%s,%s,NULL,1000,%s)',[employee,employee,'+8490000'+str(3000+index),employee+'@test','active'])
        cursor.execute("INSERT INTO tai_khoan (ma_tai_khoan,ma_nhan_vien,mat_khau_hash,trang_thai) VALUES (%s,%s,%s,'active')",[employee,employee,encoded])
        cursor.execute('INSERT INTO phan_cong_lam_viec (ma_nhan_vien,ma_chuc_vu,ma_cua_hang) VALUES (%s,%s,%s)',[employee,'sales','S2' if employee=='OTHER' else 'S1'])
    for employee,role,scope,store in [('ADMIN','system_admin','system',None),('SELLER','sales_staff','store','S1'),('MANAGER','store_manager','store','S1'),('OTHER','sales_staff','store','S2')]:
        cursor.execute('INSERT INTO phan_cong_quyen (ma_tai_khoan,ma_vai_tro,pham_vi,ma_cua_hang,duoc_uy_quyen) VALUES (%s,%s,%s,%s,%s)',[employee,role,scope,store,employee=='ADMIN'])
    cursor.execute("INSERT INTO vai_tro VALUES ('read_region','Read region'),('hr_local','HR local')")
    cursor.execute("INSERT INTO vai_tro_quyen VALUES ('read_region','reports.read'),('read_region','sales.read'),('hr_local','employees.salary')")
    cursor.execute("INSERT INTO phan_cong_quyen (ma_tai_khoan,ma_vai_tro,pham_vi,ma_khu_vuc) VALUES ('MULTI','read_region','region',1)")
    cursor.execute("INSERT INTO phan_cong_quyen (ma_tai_khoan,ma_vai_tro,pham_vi,ma_cua_hang) VALUES ('MULTI','hr_local','store','S2')")
    conn.commit()

    @contextmanager
    def connected():
        db=mysql.connector.connect(**options,database=name)
        c=db.cursor(); c.execute("SET time_zone='+00:00'"); c.close()
        try:
            yield db
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    import app.db.helpers as helpers
    import app.repositories.auth as auth
    import app.repositories.sales as sales
    import app.routers.query_explorer as explorer
    import app.core.security as security
    for module in (helpers,auth,sales,explorer):
        monkeypatch.setattr(module,'connection',connected)
    monkeypatch.setattr(security,'settings',replace(settings,auth_token_secret=secrets.token_urlsafe(48)))
    app.dependency_overrides.clear()
    with TestClient(app) as client:
        headers={}
        for index,employee in enumerate(('ADMIN','SELLER','MANAGER','OTHER','MULTI')):
            response=client.post('/api/auth/login',json={'phone':'090000'+str(3000+index),'password':password})
            assert response.status_code==200,response.text
            headers[employee]={'Authorization':'Bearer '+response.json()['access_token']}
        yield client,headers,cursor,conn
    app.dependency_overrides.clear()


def scalar(cursor,sql,params=()):
    cursor.execute(sql,params)
    return next(iter(cursor.fetchone().values()))


def adjust(client,headers,warehouse='K1',sku='SKU1',quantity=10):
    response=client.post('/api/inventory/adjustments',headers=headers['ADMIN'],json={'warehouse_id':warehouse,'product_id':sku,'quantity':quantity,'reason':'Confirmed test count'})
    assert response.status_code==201,response.text


def sell(client,headers,employee='SELLER',**changes):
    payload={'customer_id':'C1','store_id':'S1','warehouse_id':'K1','details':[{'product_id':'SKU1','quantity':2,'discount':'1.25'}],**changes}
    return client.post('/api/orders',headers=headers[employee],json=payload)


def test_baseline_versioning_and_catalog_constraints(local_db):
    conn,cursor,*_=local_db
    apply(conn,'init')
    apply(conn,'init')
    assert scalar(cursor,'SELECT COUNT(*) FROM schema_version')==1
    assert scalar(cursor,'SELECT COUNT(*) FROM tai_khoan')==0
    cursor.execute("INSERT INTO khu_vuc VALUES (88,'New region')")
    conn.commit()
    for sql in ["INSERT INTO khu_vuc VALUES (88,'Duplicate')",
                "INSERT INTO phan_cong_quyen (ma_tai_khoan,ma_vai_tro,pham_vi,ma_khu_vuc,ma_cua_hang) VALUES ('missing','sales_staff','store',88,'missing')"]:
        with pytest.raises(mysql.connector.Error):
            cursor.execute(sql)
        conn.rollback()
    cursor.execute("UPDATE schema_version SET checksum=REPEAT('0',64)")
    conn.commit()
    with pytest.raises(ValueError,match='checksum'):
        apply(conn,'init')


def test_fresh_demo_has_complete_prices_and_ledger_balances(local_db):
    conn,cursor,*_=local_db
    apply(conn,'init')
    run_file(conn,ROOT/'sql/data/02_seed_data.sql',False,section='demo')
    assert scalar(cursor,'SELECT COUNT(*) FROM don_hang')==2
    assert scalar(cursor,'SELECT COUNT(*) FROM phan_phoi')==2
    assert scalar(cursor,'SELECT COUNT(*) FROM bien_dong_kho')==11
    assert scalar(cursor,"SELECT COUNT(*) FROM phan_cong_quyen WHERE ma_vai_tro='system_admin'")==0
    assert scalar(cursor,"SELECT COUNT(*) FROM tai_khoan WHERE mat_khau_hash IS NOT NULL OR trang_thai<>'locked'")==0
    assert scalar(cursor,"SELECT COUNT(*) FROM chi_tiet_don_hang WHERE don_gia_ban IS NULL OR giam_gia IS NULL")==0
    assert scalar(cursor,"SELECT COUNT(*) FROM ton_kho tk LEFT JOIN (SELECT ma_kho,ma_san_pham,SUM(so_luong) AS q FROM bien_dong_kho GROUP BY ma_kho,ma_san_pham) b ON b.ma_kho=tk.ma_kho AND b.ma_san_pham=tk.ma_san_pham WHERE tk.so_luong<>COALESCE(b.q,0)")==0
    assert scalar(cursor,"SELECT so_luong FROM ton_kho WHERE ma_kho='DEMO-K1' AND ma_san_pham='DEMO-SKU1'")==18
    assert scalar(cursor,"SELECT don_gia_ban FROM chi_tiet_don_hang WHERE ma_don_hang='DEMO-O1' AND ma_san_pham='DEMO-SKU1'")==599000


def test_reset_dev_uses_exact_local_config_and_rebuilds_demo(local_db,tmp_path,monkeypatch):
    _,_,options,_=local_db
    name='fashion_dev_'+uuid4().hex
    admin=mysql.connector.connect(**options)
    cursor=admin.cursor()
    try:
        cursor.execute(f'CREATE DATABASE `{name}`')
        cursor.execute(f'CREATE TABLE `{name}`.obsolete_marker (id INT)')
        config=tmp_path/'dev.local.env'
        config.write_text(f'APP_ENV=development\nDB_HOST=127.0.0.1\nDB_PORT=3308\nDB_NAME={name}\nDB_USER=root\n',encoding='utf-8')
        monkeypatch.setenv('FASHION_LOCAL_DB_PASSWORD','')
        monkeypatch.setattr(sys,'argv',['database.py','reset-dev','--database',name,'--host','127.0.0.1','--port','3308','--user','root','--config',str(config),'--demo'])
        database_main()
        cursor.execute(f'SELECT version FROM `{name}`.schema_version')
        assert cursor.fetchone()[0]==3
        cursor.execute(f'SELECT COUNT(*) FROM `{name}`.don_hang')
        assert cursor.fetchone()[0]==2
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=%s AND table_name='obsolete_marker'",[name])
        assert cursor.fetchone()[0]==0
    finally:
        cursor.execute(f'DROP DATABASE IF EXISTS `{name}`')
        cursor.close();admin.close()


def test_first_admin_bootstrap_uses_operator_password_and_is_one_time(local_db,monkeypatch):
    conn,cursor,_,name=local_db
    apply(conn,'init');run_file(conn,ROOT/'sql/data/02_seed_data.sql',False,section='demo')
    from scripts import provision_account
    password=secrets.token_urlsafe(24)
    monkeypatch.setenv('FASHION_LOCAL_DB_PASSWORD','')
    monkeypatch.setattr(provision_account.getpass,'getpass',lambda prompt:password)
    monkeypatch.setattr(sys,'argv',['provision_account.py','--database',name,'--port','3308',
        '--employee','DEMO-ADMIN','--account','DEMO-ADMIN','--bootstrap-admin'])
    provision_account.main()
    cursor.execute("SELECT mat_khau_hash,trang_thai FROM tai_khoan WHERE ma_tai_khoan='DEMO-ADMIN'")
    account=cursor.fetchone()
    assert account['trang_thai']=='active'
    assert password not in account['mat_khau_hash'] and verify_password(password,account['mat_khau_hash'])
    assert scalar(cursor,"SELECT COUNT(*) FROM phan_cong_quyen WHERE ma_tai_khoan='DEMO-ADMIN' AND ma_vai_tro='system_admin'")==1
    with pytest.raises(ValueError,match='already exists'):
        provision_account.main()


def test_sales_snapshot_stock_rollback_and_idempotent_cancellation(api):
    client,headers,cursor,conn=api
    adjust(client,headers)
    response=sell(client,headers)
    assert response.status_code==201,response.text
    code=response.json()['order_id']
    conn.commit()
    assert scalar(cursor,"SELECT so_luong FROM ton_kho WHERE ma_kho='K1' AND ma_san_pham='SKU1'")==8
    cursor.execute("UPDATE san_pham SET gia_san_pham=999 WHERE ma_san_pham='SKU1'");conn.commit()
    detail=client.get('/api/orders/'+code,headers=headers['SELLER']).json()
    assert float(detail['details'][0]['don_gia_ban'])==100.50
    dashboard=client.get('/api/analytics/sales',headers=headers['MANAGER'])
    assert dashboard.status_code==200,dashboard.text
    assert float(dashboard.json()['total_revenue'])==199.75
    before=scalar(cursor,'SELECT COUNT(*) FROM don_hang');conn.commit()
    assert sell(client,headers,details=[{'product_id':'SKU1','quantity':100}]).status_code==409
    assert sell(client,headers,details=[{'product_id':'SKU1','quantity':1,'discount':'10000'}]).status_code==422
    conn.commit()
    assert scalar(cursor,'SELECT COUNT(*) FROM don_hang')==before
    for _ in range(2):
        assert client.post('/api/orders/'+code+'/cancel',headers=headers['MANAGER']).status_code==200
    conn.commit()
    assert scalar(cursor,"SELECT so_luong FROM ton_kho WHERE ma_kho='K1' AND ma_san_pham='SKU1'")==10
    assert scalar(cursor,"SELECT COUNT(*) FROM bien_dong_kho WHERE loai='cancel_sale'")==1


def test_every_read_and_export_obeys_its_own_permission_scope(api):
    client,headers,cursor,conn=api
    adjust(client,headers);adjust(client,headers,'K2')
    first=sell(client,headers).json()['order_id']
    other=sell(client,headers,'OTHER',store_id='S2',warehouse_id='K2').json()['order_id']
    assert client.get('/api/orders/'+first,headers=headers['OTHER']).status_code==404
    assert [r['ma_don_hang'] for r in client.get('/api/orders',headers=headers['MULTI']).json()['items']]==[first]
    export=client.get('/api/orders/export',headers=headers['MULTI'])
    assert first in export.text and other not in export.text
    assert client.put('/api/employees/SELLER/salary',headers=headers['MULTI'],json={'salary':1200}).status_code==404
    assert client.put('/api/employees/OTHER/salary',headers=headers['MULTI'],json={'salary':1200}).status_code==200
    assert client.post('/api/access/assignments',headers=headers['MANAGER'],json={}).status_code==403
    assert sell(client,headers,store_id='S2',warehouse_id='K2').status_code==403


def test_transfers_and_cancellations_are_balanced_and_atomic(api):
    client,headers,cursor,conn=api
    adjust(client,headers,'KC')
    payload={'source_id':'KC','target_id':'K1','details':[{'product_id':'SKU1','quantity':4}]}
    response=client.post('/api/inventory/transfers',headers=headers['ADMIN'],json=payload)
    assert response.status_code==201,response.text
    code=response.json()['transfer_id']
    conn.commit()
    assert scalar(cursor,"SELECT SUM(so_luong) FROM ton_kho WHERE ma_san_pham='SKU1'")==10
    assert client.post('/api/inventory/transfers',headers=headers['SELLER'],json=payload).status_code==403
    for _ in range(2):
        assert client.post('/api/inventory/transfers/'+code+'/cancel',headers=headers['ADMIN']).status_code==200
    conn.commit()
    assert scalar(cursor,"SELECT so_luong FROM ton_kho WHERE ma_kho='KC' AND ma_san_pham='SKU1'")==10
    assert scalar(cursor,'SELECT SUM(so_luong) FROM bien_dong_kho WHERE ma_phan_phoi=%s',[code])==0


def test_deactivation_preserves_history_and_invalidates_existing_tokens(api):
    client,headers,cursor,conn=api
    adjust(client,headers)
    code=sell(client,headers).json()['order_id']
    response=client.delete('/api/employees/SELLER',headers=headers['MANAGER'])
    assert response.status_code==200,response.text
    assert client.get('/api/auth/me',headers=headers['SELLER']).status_code==401
    conn.commit()
    assert scalar(cursor,"SELECT COUNT(*) FROM nhan_vien WHERE ma_nhan_vien='SELLER'")==1
    assert scalar(cursor,'SELECT COUNT(*) FROM don_hang WHERE ma_don_hang=%s',[code])==1


def test_granting_is_explicit_and_cannot_exceed_authority(api):
    client,headers,cursor,conn=api
    payload={'ma_tai_khoan':'SELLER','ma_vai_tro':'sales_staff','pham_vi':'store','ma_cua_hang':'S2','tu_ngay':(datetime.now(timezone.utc)+timedelta(seconds=1)).isoformat()}
    response=client.post('/api/access/assignments',headers=headers['ADMIN'],json=payload)
    assert response.status_code==201,response.text
    assert client.post('/api/access/assignments',headers=headers['MANAGER'],json=payload).status_code==403
    assert client.get('/api/query-explorer',headers=headers['SELLER']).status_code==403


def test_actual_sql_constraints_and_academic_queries(api):
    client,headers,cursor,conn=api
    for sql in ["INSERT INTO san_pham VALUES ('DUP','M1','Black','39',10,'active')",
                "INSERT INTO ton_kho VALUES ('K1','SKU1',-1)",
                "INSERT INTO phan_cong_quyen (ma_tai_khoan,ma_vai_tro,pham_vi,ma_khu_vuc,ma_cua_hang) VALUES ('SELLER','sales_staff','store',1,'S1')",
                "INSERT INTO phan_cong_quyen (ma_tai_khoan,ma_vai_tro,pham_vi,ma_cua_hang) VALUES ('SELLER','sales_staff','store','MISSING')"]:
        with pytest.raises(mysql.connector.Error):
            cursor.execute(sql)
        conn.rollback()
    for query in load_academic_queries(ROOT/'sql/query').values():
        cursor.execute(query.sql)
        cursor.fetchall()


def test_concurrent_sales_cannot_oversell_or_leave_partial_orders(api):
    from concurrent.futures import ThreadPoolExecutor
    client,headers,cursor,conn=api
    adjust(client,headers)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(sell,client,headers,details=[{'product_id':'SKU1','quantity':8}]) for _ in range(2)]
        assert sorted(f.result().status_code for f in futures)==[201,409]
    conn.commit()
    assert scalar(cursor,"SELECT so_luong FROM ton_kho WHERE ma_kho='K1' AND ma_san_pham='SKU1'")==2
    assert scalar(cursor,'SELECT COUNT(*) FROM don_hang')==1
    assert scalar(cursor,"SELECT COUNT(*) FROM bien_dong_kho WHERE loai='sale'")==1


def test_authority_is_reloaded_for_revoked_and_future_assignments(api):
    client,headers,cursor,conn=api
    cursor.execute("UPDATE phan_cong_quyen SET thu_hoi_luc=UTC_TIMESTAMP() WHERE ma_tai_khoan='SELLER'")
    conn.commit()
    assert client.get('/api/orders',headers=headers['SELLER']).status_code==403
    cursor.execute("UPDATE phan_cong_quyen SET thu_hoi_luc=NULL,tu_ngay=UTC_TIMESTAMP()+INTERVAL 1 DAY WHERE ma_tai_khoan='SELLER'")
    conn.commit()
    assert client.get('/api/orders',headers=headers['SELLER']).status_code==403


def test_work_transfer_preserves_transaction_store_and_does_not_move_permissions(api):
    client,headers,cursor,conn=api
    adjust(client,headers)
    code=sell(client,headers).json()['order_id']
    cursor.execute("UPDATE phan_cong_lam_viec SET tu_ngay=UTC_TIMESTAMP()-INTERVAL 1 DAY WHERE ma_nhan_vien='SELLER'")
    conn.commit()
    assert client.post('/api/employees/SELLER/work',headers=headers['MANAGER'],json={'store_id':'S2'}).status_code==403
    response=client.post('/api/employees/SELLER/work',headers=headers['ADMIN'],json={'store_id':'S2'})
    assert response.status_code==200,response.text
    assert client.get('/api/orders/'+code,headers=headers['MANAGER']).status_code==200
    assert client.get('/api/orders/'+code,headers=headers['OTHER']).status_code==404
    # Location history and authorization are deliberately independent.
    assert sell(client,headers,store_id='S2',warehouse_id='K2').status_code==403
    conn.commit()
    assert scalar(cursor,"SELECT COUNT(*) FROM phan_cong_lam_viec WHERE ma_nhan_vien='SELLER'")==2


def test_employee_account_password_scope_revoke_and_session_invalidation(api):
    client,headers,cursor,conn=api
    admin=headers['ADMIN']
    password=secrets.token_urlsafe(20)
    employee=client.post('/api/employees',headers=admin,json={
        'employee_id':'NEW','name':'New employee','phone':'090 123 4567',
        'email':'new@example.test','store_id':'S1','position_id':'sales','salary':'1000.00'})
    assert employee.status_code==201,employee.text
    cursor.execute("SELECT so_dien_thoai FROM nhan_vien WHERE ma_nhan_vien='NEW'")
    assert cursor.fetchone()['so_dien_thoai']=='+84901234567'
    duplicate=client.post('/api/employees',headers=admin,json={
        'employee_id':'DUP','name':'Duplicate','phone':'+84 901 234 567',
        'email':'dup@example.test','store_id':'S1','position_id':'sales','salary':'1000.00'})
    assert duplicate.status_code==409
    created=client.post('/api/access/accounts',headers=admin,json={
        'employee_id':'NEW','account_id':'NEW','password':password})
    assert created.status_code==201,created.text
    listed=client.get('/api/access/accounts',headers=admin)
    assert listed.status_code==200
    assert 'mat_khau_hash' not in listed.text and password not in listed.text
    scopes=client.get('/api/access/scopes',headers=admin)
    assert scopes.status_code==200 and scopes.json()['system_allowed']
    assert {s['ma_cua_hang'] for s in scopes.json()['stores']}=={'S1','S2'}
    login=client.post('/api/auth/login',json={'phone':'84901234567','password':password})
    assert login.status_code==200,login.text
    token={'Authorization':'Bearer '+login.json()['access_token']}
    assert login.json()['user']['assignments']==[]
    assert login.json()['user']['email']=='new@example.test'
    assert login.json()['user']['workplaces'][0]['ma_chuc_vu']=='sales'
    assert client.get('/api/auth/me',headers=token).status_code==200
    assert client.get('/api/products',headers=token).status_code==403
    assert client.get('/api/employees',headers=token).status_code==403
    grant=client.post('/api/access/assignments',headers=admin,json={
        'ma_tai_khoan':'NEW','ma_vai_tro':'sales_staff','pham_vi':'store',
        'ma_cua_hang':'S1','tu_ngay':datetime.now(timezone.utc).isoformat()})
    assert grant.status_code==201,grant.text
    assert client.get('/api/products',headers=token).status_code==200
    assert client.post('/api/orders',headers=token,json={
        'customer_id':'C1','store_id':'S2','warehouse_id':'K2',
        'details':[{'product_id':'SKU1','quantity':1}]}).status_code==403
    revoke=client.post(f"/api/access/assignments/{grant.json()['assignment_id']}/revoke",headers=admin)
    assert revoke.status_code==200,revoke.text
    assert client.get('/api/products',headers=token).status_code==403
    new_password=secrets.token_urlsafe(20)
    changed=client.put('/api/access/accounts/NEW/password',headers=admin,json={'password':new_password})
    assert changed.status_code==200,changed.text
    assert client.get('/api/auth/me',headers=token).status_code==401
    assert client.post('/api/auth/login',json={'phone':'0901234567','password':password}).status_code==401
    relogin=client.post('/api/auth/login',json={'phone':'0901234567','password':new_password})
    assert relogin.status_code==200
    renewed={'Authorization':'Bearer '+relogin.json()['access_token']}
    locked=client.put('/api/access/accounts/NEW/status',headers=admin,json={'status':'locked'})
    assert locked.status_code==200,locked.text
    assert client.get('/api/auth/me',headers=renewed).status_code==401
    assert client.post('/api/auth/login',json={'phone':'0901234567','password':new_password}).status_code==401
    activated=client.put('/api/access/accounts/NEW/status',headers=admin,json={'status':'active'})
    assert activated.status_code==200,activated.text
    assert client.get('/api/auth/me',headers=renewed).status_code==401
    relogin=client.post('/api/auth/login',json={'phone':'0901234567','password':new_password})
    assert relogin.status_code==200
    assert client.get('/api/products',headers={'Authorization':'Bearer '+relogin.json()['access_token']}).status_code==403

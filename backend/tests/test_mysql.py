"""Integration trên MySQL thử nghiệm riêng, không dùng database trong .env mặc định.

FASHION_TEST_MYSQL=1 DB_HOST=127.0.0.1 DB_PORT=3308 DB_USER=root DB_PASSWORD=''
"""
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.academic_queries import load_academic_queries
from app.db.helpers import rows, transaction
from main import app
from scripts.database import run_file

pytestmark=pytest.mark.skipif(os.getenv('FASHION_TEST_MYSQL')!='1', reason='Opt-in isolated MySQL integration test')
ROOT=Path(__file__).resolve().parents[2]


@pytest.fixture(scope='module')
def client():
    assert settings.db_host=='127.0.0.1' and settings.db_port==3308, 'Use the isolated local test server only'
    import mysql.connector
    conn=mysql.connector.connect(host=settings.db_host,port=settings.db_port,user=settings.db_user,password=settings.db_password)
    for name in ('1.TaoCoSoDuLieu.sql','2.ThemDuLieu.sql'):
        run_file(conn,ROOT/'sql'/name,False)
    conn.close()
    with TestClient(app) as test_client:
        yield test_client


def h(employee='NV000'):
    return {'X-Employee-Id':employee}


def employee_payload(client,employee_id):
    all_employees=client.get('/api/employees?limit=500',headers=h()).json()['items']
    row=next(row for row in all_employees if row['ma_nhan_vien']==employee_id)
    row.pop('ten_cua_hang',None)
    return row


@pytest.mark.parametrize('employee_id,stores,region',[
    ('NV000',20,None),('NV001',10,1),('NV002',5,2),('NV003',5,3),('NV004',1,1),('NV024',1,1),
])
def test_store_scope(client,employee_id,stores,region):
    response=client.get('/api/stores?limit=500',headers=h(employee_id))
    assert response.status_code==200,response.text
    data=response.json()
    assert data['total']==stores
    assert all(region is None or row['khu_vuc']==region for row in data['items'])


@pytest.mark.parametrize('endpoint',['employees','reports?start=2026-01-01&end=2026-12-31','queries'])
def test_staff_cannot_access_management(client,endpoint):
    assert client.get('/api/'+endpoint,headers=h('NV024')).status_code==403


def test_manager_edits_salary_and_demotes_only_own_subordinate(client):
    payload=employee_payload(client,'NV024')
    original=payload.copy()
    payload.update(luong=5500000,cap_bac=1)
    result=client.put('/api/employees/NV024',headers=h('NV004'),json=payload)
    assert result.status_code==200,result.text
    assert result.json()['cap_bac']==1
    assert client.put('/api/employees/NV024',headers=h('NV005'),json=payload).status_code==403
    assert client.put('/api/employees/NV024',headers=h('NV002'),json=payload).status_code==403
    assert client.put('/api/employees/NV024',headers=h('NV024'),json=payload).status_code==403
    assert client.put('/api/employees/NV024',headers=h('NV000'),json=original).status_code==200


def test_cannot_promote_to_equal_or_higher_role(client):
    payload=employee_payload(client,'NV024')
    payload.update(quyen_han='regional_manager',ma_cua_hang=None,khu_vuc_quan_ly=1,ma_quan_ly='NV000')
    assert client.put('/api/employees/NV024',headers=h('NV001'),json=payload).status_code==403
    assert client.put('/api/employees/NV024',headers=h('NV004'),json=payload).status_code==403


def test_replacement_is_atomic_reparents_staff_and_records_history(client):
    original=employee_payload(client,'NV004')
    new=dict(ma_nhan_vien='NV_TEST_MGR',ho_ten='Quản lý thay thế',so_dien_thoai='0999000101',email='test-manager@example.com',ma_cua_hang='CH001',ma_quan_ly='NV001',quyen_han='store_manager',khu_vuc_quan_ly=None,luong=14000000,cap_bac=3,trang_thai='active')
    response=client.post('/api/employees',headers=h('NV001'),json=new)
    assert response.status_code==200,response.text
    assert rows("SELECT COUNT(*) AS n FROM nhan_vien WHERE ma_cua_hang='CH001' AND quyen_han='store_manager' AND trang_thai='active'")[0]['n']==1
    assert rows("SELECT ma_quan_ly FROM nhan_vien WHERE ma_nhan_vien='NV024'")[0]['ma_quan_ly']=='NV_TEST_MGR'
    # Restore manager through the same appointment flow.
    assert client.put('/api/employees/NV004',headers=h('NV001'),json=original).status_code==200
    with transaction() as cursor:
        cursor.execute("DELETE FROM lich_su_quan_ly WHERE ma_nhan_vien='NV_TEST_MGR'")
    assert client.delete('/api/employees/NV_TEST_MGR',headers=h()).status_code==200


def order_payload(code='DH_TEST'):
    return dict(ma_don_hang=code,ma_nhan_vien='NV024',ma_khach_hang='KH001',ngay_tao_don='2026-10-25T10:00:00',chi_tiet=[dict(ma_san_pham='SP001',so_luong=2),dict(ma_san_pham='SP002',so_luong=1)])


def test_order_total_price_snapshot_update_and_delete(client):
    payload=order_payload()
    result=client.post('/api/orders',headers=h('NV024'),json=payload)
    assert result.status_code==200,result.text
    price=int(result.json()['chi_tiet'][0]['don_gia_ban'])
    with transaction() as cursor:
        cursor.execute("UPDATE san_pham SET gia_san_pham=999999 WHERE ma_san_pham='SP001'")
    payload['chi_tiet'][0]['so_luong']=3
    result=client.put('/api/orders/DH_TEST',headers=h('NV024'),json=payload)
    assert result.status_code==200,result.text
    assert int(result.json()['chi_tiet'][0]['don_gia_ban'])==price
    assert int(result.json()['tong_tien'])==3*price+159000
    assert client.get('/api/orders/DH_TEST',headers=h('NV029')).status_code==404
    assert client.delete('/api/orders/DH_TEST',headers=h('NV024')).status_code==200
    with transaction() as cursor:
        cursor.execute("UPDATE san_pham SET gia_san_pham=%s WHERE ma_san_pham='SP001'",(price,))


@pytest.mark.parametrize('change,expected',[
    ({'ma_khach_hang':'KH_MISSING'},400),
    ({'ma_nhan_vien':'NV029'},403),
    ({'chi_tiet':[]},422),
    ({'chi_tiet':[{'ma_san_pham':'SP001','so_luong':0}]},422),
    ({'chi_tiet':[{'ma_san_pham':'SP001','so_luong':1}]*2},422),
    ({'chi_tiet':[{'ma_san_pham':'SP_MISSING','so_luong':1}]},400),
])
def test_invalid_order_never_leaves_header(client,change,expected):
    payload=order_payload('DH_INVALID')
    payload.update(change)
    response=client.post('/api/orders',headers=h('NV024'),json=payload)
    assert response.status_code==expected,response.text
    assert not rows("SELECT * FROM don_hang WHERE ma_don_hang='DH_INVALID'")


def test_failed_update_restores_old_order_and_details(client):
    payload=order_payload('DH_ROLLBACK')
    assert client.post('/api/orders',headers=h('NV024'),json=payload).status_code==200
    before=client.get('/api/orders/DH_ROLLBACK',headers=h('NV024')).json()
    payload['ma_khach_hang']='MISSING'
    assert client.put('/api/orders/DH_ROLLBACK',headers=h('NV024'),json=payload).status_code==400
    assert client.get('/api/orders/DH_ROLLBACK',headers=h('NV024')).json()==before
    assert client.delete('/api/orders/DH_ROLLBACK',headers=h('NV024')).status_code==200


def test_distribution_requires_receiver_in_same_store(client):
    payload=dict(ma_phan_phoi='PP_TEST',ma_cua_hang='CH001',ma_nhan_vien='NV029',ngay_phan_phoi='2026-10-25',chi_tiet=[dict(ma_san_pham='SP001',so_luong=5)])
    assert client.post('/api/distributions',headers=h(),json=payload).status_code==400
    payload['ma_nhan_vien']='NV024'
    assert client.post('/api/distributions',headers=h('NV004'),json=payload).status_code==403
    assert client.post('/api/distributions',headers=h('NV001'),json=payload).status_code==200
    assert client.get('/api/distributions/PP_TEST',headers=h('NV024')).json()['chi_tiet'][0]['so_luong']==5
    assert client.get('/api/distributions/PP_TEST',headers=h('NV029')).status_code==404
    assert client.delete('/api/distributions/PP_TEST',headers=h('NV001')).status_code==200


@pytest.mark.parametrize('group',['day','month','store','employee','region'])
def test_report_revenue_is_scoped_and_totals_match(client,group):
    params='?start=2026-01-01&end=2026-12-31&group=store'
    admin=client.get('/api/reports'+params,headers=h()).json()
    north=client.get('/api/reports'+params,headers=h('NV001')).json()
    shop=client.get('/api/reports'+params,headers=h('NV004')).json()
    assert admin['total_orders']==100
    assert admin['total_revenue']>=north['total_revenue']>=shop['total_revenue']>0
    assert {r['ma'] for r in shop['sales']}=={'CH001'}
    grouped=client.get(f'/api/reports?start=2026-01-01&end=2026-12-31&group={group}',headers=h('NV001'))
    assert grouped.status_code==200,grouped.text
    assert grouped.json()['total_revenue']==north['total_revenue']


def test_seed_counts_queries_and_repeatable_migration(client):
    for table in ('danh_muc','san_pham','cua_hang','nhan_vien','phan_phoi','chi_tiet_phan_phoi','khach_hang','don_hang','chi_tiet_don_hang','lich_su_quan_ly'):
        assert rows(f'SELECT COUNT(*) AS n FROM {table}')[0]['n']>=20
    registry=load_academic_queries(ROOT/'sql'/'query')
    for query in registry.values():
        rows(query.sql)
    from app.db.connection import connection
    with connection() as conn:
        run_file(conn,ROOT/'sql'/'4.CapNhatPhanQuyen.sql',False)
        run_file(conn,ROOT/'sql'/'4.CapNhatPhanQuyen.sql',False)
    assert client.get('/api/queries/M01_Q01',headers=h()).status_code==200
    assert client.get('/api/queries/MISSING',headers=h()).status_code==404


def test_referenced_delete_rejected_and_phone_duplicates_rejected(client):
    assert client.delete('/api/categories/DM001',headers=h()).status_code==409
    payload=dict(ma_khach_hang='KH_DUP',ho_ten='Trùng số',so_dien_thoai='0983000001')
    assert client.post('/api/customers',headers=h('NV024'),json=payload).status_code==409


def test_legacy_migration_adds_roles_once_and_preserves_prices(client):
    """Recreate the old shape in a second local database, then run migration twice."""
    import mysql.connector
    from scripts.database import statements
    legacy='fashion_legacy_test'
    conn=mysql.connector.connect(host=settings.db_host,port=settings.db_port,user=settings.db_user,password=settings.db_password)
    cursor=conn.cursor(dictionary=True)
    try:
        for name in ('1.TaoCoSoDuLieu.sql','2.ThemDuLieu.sql'):
            for statement in statements(ROOT/'sql'/name):
                cursor.execute(statement.replace('quan_ly_chuoi_thoi_trang',legacy))
                if cursor.with_rows:
                    cursor.fetchall()
        conn.commit()
        cursor.execute('DROP TABLE lich_su_quan_ly')
        cursor.execute('ALTER TABLE phan_phoi ADD COLUMN ma_cua_hang VARCHAR(20) NULL')
        cursor.execute('UPDATE phan_phoi pp JOIN nhan_vien nv ON nv.ma_nhan_vien=pp.ma_nhan_vien SET pp.ma_cua_hang=nv.ma_cua_hang')
        cursor.execute('ALTER TABLE phan_phoi MODIFY COLUMN ma_cua_hang VARCHAR(20) NOT NULL,ADD CONSTRAINT legacy_pp_store FOREIGN KEY (ma_cua_hang) REFERENCES cua_hang(ma_cua_hang)')
        cursor.execute('ALTER TABLE nhan_vien DROP INDEX uq_mot_chu_thuong_hieu,DROP INDEX uq_quan_ly_khu_vuc,DROP INDEX uq_quan_ly_cua_hang')
        cursor.execute('ALTER TABLE nhan_vien DROP CHECK ck_pham_vi, DROP CHECK ck_luong, DROP CHECK ck_cap_bac')
        cursor.execute('ALTER TABLE nhan_vien DROP COLUMN quyen_han,DROP COLUMN khu_vuc_quan_ly,DROP COLUMN luong,DROP COLUMN cap_bac,DROP COLUMN trang_thai')
        cursor.execute('ALTER TABLE chi_tiet_don_hang DROP CHECK ck_don_gia_ban,DROP COLUMN don_gia_ban')
        for _ in range(2):
            for statement in statements(ROOT/'sql'/'4.CapNhatPhanQuyen.sql'):
                cursor.execute(statement.replace('USE quan_ly_chuoi_thoi_trang','USE '+legacy))
                while True:
                    if cursor.with_rows:
                        cursor.fetchall()
                    if not cursor.nextset():
                        break
        cursor.execute('SELECT quyen_han,COUNT(*) AS n FROM nhan_vien GROUP BY quyen_han')
        assert {r['quyen_han']:r['n'] for r in cursor.fetchall()}=={'admin':1,'regional_manager':3,'store_manager':20,'staff':50}
        cursor.execute('SELECT COUNT(*) AS n FROM lich_su_quan_ly')
        assert cursor.fetchone()['n']==23
        cursor.execute('SHOW COLUMNS FROM phan_phoi')
        assert 'ma_cua_hang' not in {r['Field'] for r in cursor.fetchall()}
        cursor.execute("UPDATE chi_tiet_don_hang SET don_gia_ban=123 WHERE ma_don_hang='DH001' AND ma_san_pham=(SELECT p.ma_san_pham FROM (SELECT ma_san_pham FROM chi_tiet_don_hang WHERE ma_don_hang='DH001' LIMIT 1) p)")
        conn.commit()
        # Also support an older migration that duplicated the current product price.
        cursor.execute('ALTER TABLE san_pham ADD COLUMN gia_ban DECIMAL(15,0) NULL')
        cursor.execute('UPDATE san_pham SET gia_ban=gia_san_pham')
        cursor.execute('ALTER TABLE san_pham ADD CONSTRAINT old_price_check CHECK (gia_ban>=0)')
        for statement in statements(ROOT/'sql'/'4.CapNhatPhanQuyen.sql'):
            cursor.execute(statement.replace('USE quan_ly_chuoi_thoi_trang','USE '+legacy))
            while True:
                if cursor.with_rows:
                    cursor.fetchall()
                if not cursor.nextset():
                    break
        cursor.execute('SHOW COLUMNS FROM san_pham')
        assert 'gia_ban' not in {r['Field'] for r in cursor.fetchall()}
        cursor.execute('SELECT COUNT(*) AS n FROM chi_tiet_don_hang WHERE don_gia_ban=123')
        assert cursor.fetchone()['n']==1
    finally:
        cursor.execute(f'DROP DATABASE IF EXISTS {legacy}')
        cursor.close()
        conn.close()


@pytest.mark.parametrize('sql',[
    "UPDATE nhan_vien SET quyen_han='store_manager' WHERE ma_nhan_vien='NV024'",
    "UPDATE nhan_vien SET khu_vuc_quan_ly=1 WHERE ma_nhan_vien='NV002'",
])
def test_database_prevents_two_current_managers_for_one_scope(client,sql):
    import mysql.connector
    with pytest.raises(mysql.connector.IntegrityError):
        with transaction() as cursor:
            cursor.execute(sql)

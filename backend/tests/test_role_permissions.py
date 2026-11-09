from dataclasses import replace
from contextlib import contextmanager
from datetime import datetime,timedelta,timezone
from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.core.authentication import get_current_user
from app.core.security import hash_password,verify_password,create_access_token,decode_access_token
import app.core.security as security
import app.routers.auth as auth_router
import app.routers.access as access_router
from app.core.config import settings
from app.permissions import store_scope,warehouse_scope,grants
from app.repositories.access import assert_delegable
from app.routers.access import GrantInput
from main import app
from access_helpers import actor,grant


def test_permissions_cannot_spread_between_assignments():
    user=actor(grant(scope='region',region=99,permissions=['sales.read']),grant(store='S2',permissions=['employees.salary']))
    sql,params=store_scope(user,permission='employees.salary')
    assert 'khu_vuc' not in sql
    assert params==['S2']
    sql,params=store_scope(user,permission='sales.read')
    assert params==[99] and 'ma_cua_hang' not in sql


def test_employee_code_and_reporting_relationship_grant_nothing():
    user={'ma_nhan_vien':'NV000','quyen_han':'admin','ma_quan_ly':None,'subordinates':['E2']}
    assert store_scope(user)==('0=1',[])
    assert warehouse_scope(user)==('0=1',[])


def test_expired_future_and_revoked_assignments_are_denied():
    now=datetime.now(timezone.utc).replace(tzinfo=None)
    user=actor(grant(permissions=['sales.read'],den_ngay=now),
               grant(permissions=['sales.read'],tu_ngay=now+timedelta(days=1)),
               grant(permissions=['sales.read'],trang_thai='pending'),
               grant(permissions=['sales.read'],thu_hoi_luc=now))
    assert not list(grants(user,'sales.read',now))


def test_warehouse_scope_does_not_authorize_the_store():
    user=actor(grant(scope='warehouse',warehouse='K1',permissions=['inventory.read']))
    assert warehouse_scope(user)==('(k.ma_kho=%s)',['K1'])
    assert store_scope(user,permission='inventory.read')==('0=1',[])


def test_personnel_manager_cannot_issue_roles_or_run_global_queries():
    app.dependency_overrides[get_current_user]=lambda: actor(grant(permissions=['employees.write','employees.read','queries.execute']))
    try:
        with TestClient(app) as client:
            assert client.post('/api/access/assignments',json={}).status_code==403
            assert client.get('/api/query-explorer').status_code==403
    finally:
        app.dependency_overrides.clear()


def test_scoped_supervisor_can_create_only_an_in_scope_employee_account(monkeypatch):
    user=actor(grant(scope='store',store='S1',permissions=['employees.write']))
    app.dependency_overrides[get_current_user]=lambda:user

    class Cursor:
        def __init__(self):
            self.queries=[]
            self.employee_exists=True

        def execute(self,query,params):
            self.queries.append((query,params))

        def fetchone(self):
            return {'ma_nhan_vien':'E2'} if self.employee_exists else None

    cursor=Cursor()

    @contextmanager
    def transaction():
        yield cursor

    monkeypatch.setattr(access_router,'transaction',transaction)
    monkeypatch.setattr(access_router,'hash_password',lambda value:'hashed-password')
    try:
        with TestClient(app) as client:
            response=client.post('/api/access/accounts',json={
                'employee_id':'E2','account_id':'A2','password':'a-long-random-test-password'
            })
            assert response.status_code==201
            assert cursor.queries[0][1]==['E2','S1','S1']
            assert 'scope_ch.ma_cua_hang = %s' in cursor.queries[0][0]
            assert cursor.queries[1][1]==['A2','E2','hashed-password','active']
            cursor.employee_exists=False
            before=len(cursor.queries)
            denied=client.post('/api/access/accounts',json={
                'employee_id':'E3','account_id':'A3','password':'a-long-random-test-password'
            })
            assert denied.status_code==404
            assert len(cursor.queries)==before+1
    finally:
        app.dependency_overrides.clear()


def test_delegation_must_fit_one_assignment_including_time():
    now=datetime.now(timezone.utc).replace(tzinfo=None)
    donor=grant(scope='store',store='S1',permissions=['auth.grant','sales.read'],duoc_uy_quyen=True,den_ngay=now+timedelta(days=1))
    user=actor(donor,grant(store='S2',permissions=['employees.write']))
    target={**grant(store='S1'), 'tu_ngay':now+timedelta(seconds=1),'den_ngay':now+timedelta(hours=1)}
    assert_delegable(MagicMock(),user,target,{'sales.read'})
    for change,permissions in [({'ma_cua_hang':'S2'},{'sales.read'}), ({},{'employees.write'}), ({'den_ngay':None},{'sales.read'})]:
        with pytest.raises(HTTPException) as error:
            assert_delegable(MagicMock(),user,{**target,**change},permissions)
        assert error.value.status_code==403


def test_grant_input_validates_typed_scope_and_time():
    with pytest.raises(ValidationError):
        GrantInput(ma_tai_khoan='A',ma_vai_tro='custom',pham_vi='store',ma_khu_vuc=99,tu_ngay='2026-12-01T00:00:00Z')
    assert GrantInput(ma_tai_khoan='A',ma_vai_tro='custom',pham_vi='region',ma_khu_vuc=99,tu_ngay='2026-12-01T00:00:00Z').ma_khu_vuc==99


def test_passwords_are_salted_and_employee_id_is_not_a_password():
    first=hash_password('a-long-random-test-password')
    assert first!=hash_password('a-long-random-test-password')
    assert verify_password('a-long-random-test-password',first)
    assert not verify_password('E1',first)
    assert not verify_password('anything',None)


def test_login_and_signed_token_use_real_account_credentials(monkeypatch):
    monkeypatch.setattr(security,'settings',replace(settings,auth_token_secret='test-secret-value-that-is-at-least-32-bytes'))
    account={**actor(grant(permissions=['sales.create'])), 'mat_khau_hash':hash_password('a-long-random-test-password'),'auth_version':0}
    monkeypatch.setattr(auth_router,'get_user_by_phone',lambda phone:account)
    with TestClient(app) as client:
        assert client.post('/api/auth/login',json={'phone':'0900000000','password':'E1'}).status_code==401
        response=client.post('/api/auth/login',json={'phone':'0900000000','password':'a-long-random-test-password'})
    assert response.status_code==200
    assert 'mat_khau_hash' not in response.text
    assert response.json()['user']['assignments']
    assert decode_access_token(response.json()['access_token'])['employee_id']=='E1'


def test_user_can_change_password_and_keeps_only_a_rotated_session(monkeypatch):
    monkeypatch.setattr(security,'settings',replace(settings,auth_token_secret='test-secret-value-that-is-at-least-32-bytes'))
    account={'mat_khau_hash':hash_password('old-password-is-long-enough'),'auth_version':4}
    user=actor(grant(permissions=['sales.create']))
    user['ma_tai_khoan']='A1'
    app.dependency_overrides[get_current_user]=lambda:user

    class Cursor:
        def __init__(self):
            self.updated=False

        def execute(self,query,params):
            if query.strip().startswith('UPDATE tai_khoan'):
                account['mat_khau_hash']=params[0]
                account['auth_version']+=1
                self.updated=True

        def fetchone(self):
            return dict(account)

    cursor=Cursor()

    @contextmanager
    def transaction():
        yield cursor

    monkeypatch.setattr(auth_router,'transaction',transaction)
    tokens=[]
    monkeypatch.setattr(auth_router,'create_access_token',lambda account_id,version:(tokens.append((account_id,version)) or ('rotated-token',3600)))
    try:
        with TestClient(app) as client:
            invalid=client.post('/api/auth/password',json={
                'current_password':'wrong-password','new_password':'new-password-is-long-enough'
            })
            assert invalid.status_code==400
            assert not cursor.updated
            changed=client.post('/api/auth/password',json={
                'current_password':'old-password-is-long-enough','new_password':'new-password-is-long-enough'
            })
        assert changed.status_code==200
        assert changed.json()['access_token']=='rotated-token'
        assert tokens==[('A1',5)]
        assert verify_password('new-password-is-long-enough',account['mat_khau_hash'])
    finally:
        app.dependency_overrides.clear()

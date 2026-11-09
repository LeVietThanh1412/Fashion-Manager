from datetime import datetime,timezone
from typing import Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field,model_validator
from app.core.authentication import get_current_user,require_permissions
from app.core.security import hash_password
from app.db.helpers import rows,transaction
from app.repositories.access import grant_role
from app.permissions import employee_scope,store_scope,warehouse_scope,grants
import mysql.connector

router=APIRouter(prefix='/api/access',tags=['access'])


class GrantInput(BaseModel):
    model_config=ConfigDict(extra='forbid')
    ma_tai_khoan: str=Field(min_length=1,max_length=20)
    ma_vai_tro: str=Field(min_length=1,max_length=30)
    pham_vi: Literal['system','region','store','warehouse']
    ma_khu_vuc: int | None=None
    ma_cua_hang: str | None=Field(default=None,max_length=20)
    ma_kho: str | None=Field(default=None,max_length=20)
    tu_ngay: datetime
    den_ngay: datetime | None=None
    duoc_uy_quyen: bool=False

    @model_validator(mode='after')
    def valid(self):
        required={'system':None,'region':'ma_khu_vuc','store':'ma_cua_hang','warehouse':'ma_kho'}[self.pham_vi]
        if any((getattr(self,k) is not None)!=(k==required) for k in ('ma_khu_vuc','ma_cua_hang','ma_kho')):
            raise ValueError('Scope must identify exactly one existing entity, or the system.')
        for name in ('tu_ngay','den_ngay'):
            value=getattr(self,name)
            if value:
                if not value.tzinfo:
                    raise ValueError('Validity must include a timezone.')
                setattr(self,name,value.astimezone(timezone.utc).replace(tzinfo=None))
        if self.den_ngay and self.den_ngay<=self.tu_ngay:
            raise ValueError('Expiry must follow the start.')
        return self


class AccountInput(BaseModel):
    model_config=ConfigDict(extra='forbid')
    employee_id: str=Field(min_length=1,max_length=20)
    account_id: str=Field(min_length=1,max_length=20)
    password: str=Field(min_length=12,max_length=128)


class PasswordInput(BaseModel):
    model_config=ConfigDict(extra='forbid')
    password: str=Field(min_length=12,max_length=128)


class AccountStatusInput(BaseModel):
    model_config=ConfigDict(extra='forbid')
    status: Literal['active','locked']


def require_account_access(actor=Depends(get_current_user)):
    if not any(grants(actor,'auth.grant')) and not any(grants(actor,'employees.write')):
        raise HTTPException(403,'Permission denied: employees.write')
    return actor


def account_employee_scope(actor):
    conditions=[]
    params=[]
    for permission in ('employees.write','auth.grant'):
        if any(grants(actor,permission)):
            condition,scope_params=employee_scope(actor,permission)
            conditions.append(condition)
            params.extend(scope_params)
    return ('('+' OR '.join(conditions)+')' if conditions else '0=1'),params


@router.get('/roles')
def roles(actor=Depends(require_permissions('auth.grant'))):
    return {'roles':rows('SELECT * FROM vai_tro'),'permissions':rows('SELECT * FROM vai_tro_quyen ORDER BY ma_vai_tro,ma_quyen')}


@router.get('/accounts')
def accounts(actor=Depends(require_account_access)):
    condition,params=account_employee_scope(actor)
    people=rows(f'''SELECT nv.ma_nhan_vien,nv.ho_ten,nv.so_dien_thoai,nv.trang_thai AS employee_status,
        tk.ma_tai_khoan,tk.trang_thai AS account_status
        FROM nhan_vien nv LEFT JOIN tai_khoan tk ON tk.ma_nhan_vien=nv.ma_nhan_vien
        WHERE {condition} ORDER BY nv.ho_ten,nv.ma_nhan_vien''',params)
    ids=[p['ma_nhan_vien'] for p in people]
    if not ids:
        return {'items':[]}
    placeholders=','.join(['%s']*len(ids))
    workplaces=rows(f'''SELECT lv.ma_nhan_vien,lv.ma_chuc_vu,cv.ten_chuc_vu,lv.ma_cua_hang,lv.ma_kho,
        COALESCE(ch.ten_cua_hang,k.ten_kho) AS ten_noi_lam_viec
        FROM phan_cong_lam_viec lv JOIN chuc_vu cv ON cv.ma_chuc_vu=lv.ma_chuc_vu
        LEFT JOIN cua_hang ch ON ch.ma_cua_hang=lv.ma_cua_hang LEFT JOIN kho k ON k.ma_kho=lv.ma_kho
        WHERE lv.ma_nhan_vien IN ({placeholders}) AND lv.tu_ngay<=UTC_TIMESTAMP()
        AND (lv.den_ngay IS NULL OR UTC_TIMESTAMP()<lv.den_ngay)''',ids)
    account_ids=[p['ma_tai_khoan'] for p in people if p['ma_tai_khoan']]
    assignments=[]
    if account_ids and any(grants(actor,'auth.grant')):
        marks=','.join(['%s']*len(account_ids))
        assignments=rows(f'''SELECT pc.ma_phan_cong,pc.ma_tai_khoan,pc.ma_vai_tro,pc.pham_vi,
            pc.ma_khu_vuc,pc.ma_cua_hang,pc.ma_kho,pc.trang_thai,pc.tu_ngay,pc.den_ngay,
            pc.thu_hoi_luc,pc.duoc_uy_quyen,
            CASE WHEN pc.trang_thai='active' AND pc.thu_hoi_luc IS NULL
                AND pc.tu_ngay<=UTC_TIMESTAMP(6) AND (pc.den_ngay IS NULL OR UTC_TIMESTAMP(6)<pc.den_ngay)
                THEN TRUE ELSE FALSE END AS effective,
            GROUP_CONCAT(vq.ma_quyen ORDER BY vq.ma_quyen SEPARATOR ',') AS permission_codes
            FROM phan_cong_quyen pc JOIN vai_tro_quyen vq ON vq.ma_vai_tro=pc.ma_vai_tro
            WHERE pc.ma_tai_khoan IN ({marks}) GROUP BY pc.ma_phan_cong''',account_ids)
    for person in people:
        person['workplaces']=[w for w in workplaces if w['ma_nhan_vien']==person['ma_nhan_vien']]
        person['assignments']=[{**a,'permissions':a['permission_codes'].split(',')} for a in assignments if a['ma_tai_khoan']==person['ma_tai_khoan']]
        for a in person['assignments']:
            a.pop('permission_codes')
    return {'items':people}


@router.get('/scopes')
def scopes(actor=Depends(require_permissions('auth.grant'))):
    delegated={**actor,'assignments':[g for g in actor['assignments'] if g.get('duoc_uy_quyen')]}
    donors=list(grants(delegated,'auth.grant'))
    store_condition,store_params=store_scope(delegated,'ch','auth.grant')
    warehouse_condition,warehouse_params=warehouse_scope(delegated,'k','auth.grant')
    all_regions=any(g['pham_vi']=='system' for g in donors)
    region_ids=sorted({g['ma_khu_vuc'] for g in donors if g['pham_vi']=='region'})
    regions=rows('SELECT ma_khu_vuc,ten_khu_vuc FROM khu_vuc ORDER BY ma_khu_vuc') if all_regions else (
        rows('SELECT ma_khu_vuc,ten_khu_vuc FROM khu_vuc WHERE ma_khu_vuc IN ('+','.join(['%s']*len(region_ids))+') ORDER BY ma_khu_vuc',region_ids) if region_ids else [])
    return {'system_allowed':all_regions,'regions':regions,
        'stores':rows(f'SELECT ch.ma_cua_hang,ch.ten_cua_hang FROM cua_hang ch WHERE {store_condition} ORDER BY ch.ma_cua_hang',store_params),
        'warehouses':rows(f'SELECT k.ma_kho,k.ten_kho FROM kho k WHERE {warehouse_condition} ORDER BY k.ma_kho',warehouse_params)}


@router.post('/assignments',status_code=201)
def assign(payload: GrantInput,actor=Depends(require_permissions('auth.grant'))):
    return grant_role(actor,payload.model_dump())


@router.post('/accounts',status_code=201)
def create_account(payload: AccountInput,actor=Depends(require_account_access)):
    condition,params=account_employee_scope(actor)
    try:
        with transaction() as cursor:
            cursor.execute(f"""SELECT nv.ma_nhan_vien FROM nhan_vien nv
                WHERE nv.ma_nhan_vien=%s AND nv.trang_thai='active' AND {condition}
                FOR UPDATE""",[payload.employee_id,*params])
            if not cursor.fetchone():
                raise HTTPException(404,'Active employee missing or outside your scope.')
            cursor.execute('INSERT INTO tai_khoan (ma_tai_khoan,ma_nhan_vien,mat_khau_hash,trang_thai) VALUES (%s,%s,%s,%s)',[payload.account_id,payload.employee_id,hash_password(payload.password),'active'])
    except mysql.connector.IntegrityError as exc:
        if exc.errno==1062:
            raise HTTPException(409,'Employee already has an account or account ID exists.') from None
        raise
    return {'account_id':payload.account_id,'status':'active'}


@router.put('/accounts/{account_id}/status')
def set_account_status(account_id: str,payload: AccountStatusInput,actor=Depends(require_permissions('auth.grant',system=True))):
    if actor['ma_tai_khoan']==account_id and payload.status=='locked':
        raise HTTPException(403,'Cannot lock your own account.')
    with transaction() as cursor:
        cursor.execute('''SELECT tk.ma_tai_khoan,tk.mat_khau_hash,nv.trang_thai AS employee_status
            FROM tai_khoan tk JOIN nhan_vien nv ON nv.ma_nhan_vien=tk.ma_nhan_vien
            WHERE tk.ma_tai_khoan=%s FOR UPDATE''',[account_id])
        account=cursor.fetchone()
        if not account:
            raise HTTPException(404,'Account missing.')
        if payload.status=='active' and (not account['mat_khau_hash'] or account['employee_status']!='active'):
            raise HTTPException(409,'Set a password and activate the employee first.')
        cursor.execute('UPDATE tai_khoan SET trang_thai=%s,auth_version=auth_version+1 WHERE ma_tai_khoan=%s',[payload.status,account_id])
    return {'account_id':account_id,'status':payload.status}


@router.put('/accounts/{account_id}/password')
def reset_password(account_id: str,payload: PasswordInput,actor=Depends(require_permissions('auth.grant',system=True))):
    encoded=hash_password(payload.password)
    with transaction() as cursor:
        cursor.execute('SELECT ma_tai_khoan FROM tai_khoan WHERE ma_tai_khoan=%s FOR UPDATE',[account_id])
        if not cursor.fetchone():
            raise HTTPException(404,'Account missing.')
        cursor.execute('UPDATE tai_khoan SET mat_khau_hash=%s,auth_version=auth_version+1 WHERE ma_tai_khoan=%s',[encoded,account_id])
    return {'account_id':account_id,'status':'password_updated'}


@router.post('/assignments/{assignment_id}/revoke')
def revoke(assignment_id: int,actor=Depends(require_permissions('auth.grant',system=True))):
    # Revocation is initially restricted to system authorization administrators.
    with transaction() as cursor:
        cursor.execute('SELECT ma_tai_khoan FROM phan_cong_quyen WHERE ma_phan_cong=%s',[assignment_id])
        target=cursor.fetchone()
        if not target:
            raise HTTPException(404,'Assignment missing.')
        cursor.execute('SELECT ma_tai_khoan FROM tai_khoan WHERE ma_tai_khoan=%s FOR UPDATE',[target['ma_tai_khoan']])
        cursor.fetchone()
        cursor.execute('UPDATE phan_cong_quyen SET thu_hoi_luc=UTC_TIMESTAMP() WHERE ma_phan_cong=%s AND thu_hoi_luc IS NULL',[assignment_id])
    return {'status':'revoked'}

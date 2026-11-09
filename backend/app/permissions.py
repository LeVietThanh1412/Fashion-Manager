"""Permission and scope are evaluated together on each current assignment."""
from datetime import datetime, timezone
import re
from fastapi import HTTPException


def grants(actor, permission, now=None):
    now = now or datetime.now(timezone.utc).replace(tzinfo=None)
    for grant in actor.get('assignments', []):
        start, end = grant.get('tu_ngay'), grant.get('den_ngay')
        if isinstance(start, str):
            start = datetime.fromisoformat(start.replace('Z','+00:00'))
        if isinstance(end, str):
            end = datetime.fromisoformat(end.replace('Z','+00:00'))
        if start and start.tzinfo:
            start = start.astimezone(timezone.utc).replace(tzinfo=None)
        if end and end.tzinfo:
            end = end.astimezone(timezone.utc).replace(tzinfo=None)
        if (permission in grant.get('permissions', []) and grant.get('trang_thai','active')=='active' and not grant.get('thu_hoi_luc')
                and (not start or start <= now) and (not end or now < end)):
            yield grant


def require_permission(actor, permission):
    if not any(grants(actor, permission)):
        raise HTTPException(403, 'Permission denied: '+permission)


def has_system_permission(actor, permission):
    return any(g['pham_vi']=='system' for g in grants(actor, permission))


def _alias(alias):
    if not re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]*', alias):
        raise ValueError('Invalid SQL alias')
    return alias


def store_scope(actor, alias='ch', permission='stores.read'):
    alias = _alias(alias)
    clauses, params = [], []
    for grant in grants(actor, permission):
        scope = grant['pham_vi']
        if scope == 'system':
            return '1=1', []
        if scope == 'region':
            clauses.append(f'{alias}.khu_vuc = %s')
            params.append(grant['ma_khu_vuc'])
        elif scope == 'store':
            clauses.append(f'{alias}.ma_cua_hang = %s')
            params.append(grant['ma_cua_hang'])
        # A warehouse assignment never grants access to the entire store.
    return ('('+' OR '.join(clauses)+')' if clauses else '0=1'), params


def warehouse_scope(actor, alias='k', permission='inventory.read'):
    alias = _alias(alias)
    clauses, params = [], []
    for grant in grants(actor, permission):
        scope = grant['pham_vi']
        if scope == 'system':
            return '1=1', []
        if scope == 'warehouse':
            clauses.append(f'{alias}.ma_kho=%s')
            params.append(grant['ma_kho'])
        elif scope == 'store':
            clauses.append(f'{alias}.ma_cua_hang=%s')
            params.append(grant['ma_cua_hang'])
        elif scope == 'region':
            clauses.append(f'({alias}.ma_khu_vuc=%s OR EXISTS (SELECT 1 FROM cua_hang scope_ch WHERE scope_ch.ma_cua_hang={alias}.ma_cua_hang AND scope_ch.khu_vuc=%s))')
            params.extend([grant['ma_khu_vuc']]*2)
    return ('('+' OR '.join(clauses)+')' if clauses else '0=1'), params


def check_store(cursor, actor, store_id, permission='stores.read'):
    condition, params = store_scope(actor, permission=permission)
    cursor.execute(f"SELECT ch.* FROM cua_hang ch WHERE ch.ma_cua_hang=%s AND ch.trang_thai='active' AND {condition}", [store_id,*params])
    store = cursor.fetchone()
    if not store:
        raise HTTPException(403, 'Store outside the permitted scope.')
    return store


def check_warehouse(cursor, actor, warehouse_id, permission='inventory.read'):
    condition, params = warehouse_scope(actor,permission=permission)
    cursor.execute(f"SELECT k.* FROM kho k WHERE k.ma_kho=%s AND k.trang_thai='active' AND {condition}", [warehouse_id,*params])
    warehouse = cursor.fetchone()
    if not warehouse:
        raise HTTPException(403, 'Warehouse outside the permitted scope.')
    if warehouse['ma_cua_hang']:
        cursor.execute("SELECT trang_thai FROM cua_hang WHERE ma_cua_hang=%s", (warehouse['ma_cua_hang'],))
        if cursor.fetchone()['trang_thai'] != 'active':
            raise HTTPException(409, 'The store is inactive.')
    return warehouse


def employee_scope(actor, permission='employees.read', alias='nv'):
    _alias(alias)
    if has_system_permission(actor, permission):
        return '1=1', []
    store_condition, store_params = store_scope(actor, 'scope_ch', permission)
    wh_condition, wh_params = warehouse_scope(actor, 'scope_k', permission)
    return (f"EXISTS (SELECT 1 FROM phan_cong_lam_viec lv LEFT JOIN kho scope_k ON scope_k.ma_kho=lv.ma_kho LEFT JOIN cua_hang scope_ch ON scope_ch.ma_cua_hang=COALESCE(lv.ma_cua_hang,scope_k.ma_cua_hang) WHERE lv.ma_nhan_vien={alias}.ma_nhan_vien AND lv.tu_ngay<=UTC_TIMESTAMP() AND (lv.den_ngay IS NULL OR UTC_TIMESTAMP()<lv.den_ngay) AND ({store_condition} OR {wh_condition}))", [*store_params,*wh_params])


def check_employee(cursor, actor, employee_id, permission='employees.read'):
    condition, params = employee_scope(actor,permission)
    cursor.execute(f'SELECT nv.* FROM nhan_vien nv WHERE nv.ma_nhan_vien=%s AND {condition}', [employee_id,*params])
    employee = cursor.fetchone()
    if not employee:
        raise HTTPException(404, 'Employee outside the permitted scope.')
    return employee

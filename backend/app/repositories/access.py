from datetime import datetime,timezone
from fastapi import HTTPException
from app.db.helpers import transaction
from app.permissions import grants


def _inside(cursor, donor, target):
    if donor['pham_vi']=='system':
        return True
    if donor['pham_vi']==target['pham_vi']:
        key={'region':'ma_khu_vuc','store':'ma_cua_hang','warehouse':'ma_kho'}[donor['pham_vi']]
        return donor[key]==target[key]
    if target['pham_vi']=='store' and donor['pham_vi']=='region':
        cursor.execute('SELECT khu_vuc FROM cua_hang WHERE ma_cua_hang=%s',[target['ma_cua_hang']])
        store=cursor.fetchone()
        return bool(store and store['khu_vuc']==donor['ma_khu_vuc'])
    if target['pham_vi']=='warehouse' and donor['pham_vi'] in {'region','store'}:
        cursor.execute('SELECT k.ma_cua_hang,COALESCE(ch.khu_vuc,k.ma_khu_vuc) AS region FROM kho k LEFT JOIN cua_hang ch ON ch.ma_cua_hang=k.ma_cua_hang WHERE k.ma_kho=%s',[target['ma_kho']])
        warehouse=cursor.fetchone()
        return bool(warehouse and (warehouse['ma_cua_hang']==donor.get('ma_cua_hang') if donor['pham_vi']=='store' else warehouse['region']==donor['ma_khu_vuc']))
    return False


def assert_delegable(cursor,actor,target,permissions):
    now=datetime.now(timezone.utc).replace(tzinfo=None)
    for donor in grants(actor,'auth.grant',now):
        if not donor['duoc_uy_quyen'] or not permissions <= set(donor['permissions']):
            continue
        if target['tu_ngay']<donor['tu_ngay']:
            continue
        if donor['den_ngay'] and (target['den_ngay'] is None or target['den_ngay']>donor['den_ngay']):
            continue
        if _inside(cursor,donor,target):
            return
    raise HTTPException(403,'The role, scope or validity exceeds your delegable assignment.')


def grant_role(actor,data):
    data = dict(data)
    data['tu_ngay'] = max(data['tu_ngay'],datetime.now(timezone.utc).replace(tzinfo=None))
    if data['den_ngay'] and data['den_ngay'] <= data['tu_ngay']:
        raise HTTPException(422,'Assignment has already expired.')
    with transaction() as cursor:
        # Serialize issuance/revocation with changes to the issuer's assignments.
        cursor.execute("SELECT tk.ma_tai_khoan FROM tai_khoan tk JOIN nhan_vien nv ON nv.ma_nhan_vien=tk.ma_nhan_vien WHERE tk.ma_tai_khoan=%s AND tk.trang_thai='active' AND nv.trang_thai='active' FOR UPDATE",[actor['ma_tai_khoan']])
        if not cursor.fetchone():
            raise HTTPException(403,'Issuer account inactive.')
        # Reload authority in this transaction; no stale request snapshot may grant roles.
        cursor.execute('''SELECT pc.*,vq.ma_quyen FROM phan_cong_quyen pc
            JOIN vai_tro_quyen vq ON vq.ma_vai_tro=pc.ma_vai_tro WHERE pc.ma_tai_khoan=%s
            AND pc.thu_hoi_luc IS NULL AND pc.tu_ngay<=UTC_TIMESTAMP(6)
            AND pc.trang_thai='active'
            AND (pc.den_ngay IS NULL OR UTC_TIMESTAMP(6)<pc.den_ngay)''',[actor['ma_tai_khoan']])
        assignments={}
        for row in cursor.fetchall():
            grant=assignments.setdefault(row['ma_phan_cong'],{k:v for k,v in row.items() if k!='ma_quyen'})
            grant.setdefault('permissions',[]).append(row['ma_quyen'])
        cursor.execute('SELECT ma_quyen FROM vai_tro_quyen WHERE ma_vai_tro=%s',[data['ma_vai_tro']])
        permissions={r['ma_quyen'] for r in cursor.fetchall()}
        if not permissions:
            raise HTTPException(422,'Unknown or empty role.')
        assert_delegable(cursor,{**actor,'assignments':list(assignments.values())},data,permissions)
        cursor.execute('SELECT ma_tai_khoan FROM tai_khoan WHERE ma_tai_khoan=%s',[data['ma_tai_khoan']])
        if not cursor.fetchone():
            raise HTTPException(404,'Account missing.')
        cursor.execute('''INSERT INTO phan_cong_quyen
            (ma_tai_khoan,ma_vai_tro,pham_vi,ma_khu_vuc,ma_cua_hang,ma_kho,tu_ngay,den_ngay,duoc_uy_quyen,nguoi_cap)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            [data[k] for k in ('ma_tai_khoan','ma_vai_tro','pham_vi','ma_khu_vuc','ma_cua_hang','ma_kho','tu_ngay','den_ngay','duoc_uy_quyen')]+[actor['ma_tai_khoan']])
        return {'assignment_id':cursor.lastrowid}

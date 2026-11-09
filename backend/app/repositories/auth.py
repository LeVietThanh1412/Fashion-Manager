from app.db.connection import connection, loader
from app.core.phone import normalize_phone


def _get(query, params):
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(loader.load(query), params)
            user = cursor.fetchone()
            if not user:
                return None
            cursor.execute(loader.load('auth/assignments.sql'), {'account_id':user['ma_tai_khoan']})
            assignments = {}
            for row in cursor.fetchall():
                grant = assignments.setdefault(row['ma_phan_cong'], {k:v for k,v in row.items() if k!='ma_quyen'})
                grant.setdefault('permissions',[]).append(row['ma_quyen'])
            user['assignments'] = list(assignments.values())
            cursor.execute('''SELECT lv.ma_chuc_vu,cv.ten_chuc_vu,lv.ma_cua_hang,lv.ma_kho,
                COALESCE(ch.ten_cua_hang,k.ten_kho) AS ten_noi_lam_viec,lv.tu_ngay,lv.den_ngay
                FROM phan_cong_lam_viec lv JOIN chuc_vu cv ON cv.ma_chuc_vu=lv.ma_chuc_vu
                LEFT JOIN cua_hang ch ON ch.ma_cua_hang=lv.ma_cua_hang LEFT JOIN kho k ON k.ma_kho=lv.ma_kho
                WHERE lv.ma_nhan_vien=%s AND lv.tu_ngay<=UTC_TIMESTAMP()
                AND (lv.den_ngay IS NULL OR UTC_TIMESTAMP()<lv.den_ngay)
                ORDER BY lv.tu_ngay DESC''',[user['ma_nhan_vien']])
            user['workplaces'] = cursor.fetchall()
            # Display-only summaries; authorization always reads assignments.
            user['quyen_han'] = next((g['ma_vai_tro'] for g in assignments.values()), 'unassigned')
            user['ma_cua_hang'] = None
            user['khu_vuc_quan_ly'] = None
            user['store_region'] = None
            return user
        finally:
            cursor.close()


def get_user_by_phone(phone):
    return _get('auth/by_phone.sql', {'phone':normalize_phone(phone)})


def get_user_by_id(account_id):
    return _get('auth/by_id.sql', {'account_id':account_id})

from datetime import datetime,timedelta,timezone


def grant(role='sales_staff',scope='store',store='S1',region=None,warehouse=None,permissions=(),**changes):
    now=datetime.now(timezone.utc).replace(tzinfo=None)
    return {'ma_vai_tro':role,'pham_vi':scope,'ma_cua_hang':store if scope=='store' else None,
            'ma_khu_vuc':region if scope=='region' else None,'ma_kho':warehouse if scope=='warehouse' else None,
            'tu_ngay':now-timedelta(days=1),'den_ngay':None,'thu_hoi_luc':None,
            'duoc_uy_quyen':False,'permissions':list(permissions),**changes}


def actor(*assignments,employee='E1'):
    return {'ma_tai_khoan':employee,'ma_nhan_vien':employee,'ho_ten':'Test User',
            'so_dien_thoai':'0900000000','trang_thai':'active','assignments':list(assignments),
            'quyen_han':assignments[0]['ma_vai_tro'] if assignments else 'unassigned',
            'ma_cua_hang':None,'khu_vuc_quan_ly':None,'store_region':None}

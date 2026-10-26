"""Read-only API/CORS checks, optionally logging in with SMOKE_PHONE/SMOKE_PASSWORD."""
import argparse
import os

import httpx

PUBLIC_PATHS = ('/health', '/api/health/db', '/api/products?limit=100', '/api/categories')
PROTECTED_PATHS = (
    '/api/auth/me', '/api/stores', '/api/analytics/summary', '/api/analytics/sales',
    '/api/employees', '/api/employees/stores', '/api/customers',
    '/api/employee/distribution', '/api/query-explorer',
)
MANAGER_PATHS = (
    '/api/stores', '/api/analytics/summary', '/api/analytics/sales',
    '/api/employees', '/api/employees/stores',
)
STAFF_PATHS = ('/api/customers', '/api/employee/distribution')


def verify_api(client, origin: str, phone: str = '', password: str = '') -> None:
    """Accept httpx.Client or FastAPI TestClient so CI and local checks match."""
    if bool(phone) != bool(password):
        raise ValueError('Set both SMOKE_PHONE and SMOKE_PASSWORD to test login.')

    def check(method, path, expected=200, **kwargs):
        response = client.request(method, path, headers={'Origin': origin, **kwargs.pop('headers', {})}, **kwargs)
        if response.headers.get('access-control-allow-origin') != origin:
            raise ValueError(f'CORS does not allow {origin} for {path}. Check APP_CORS_ORIGINS.')
        if response.status_code != expected:
            raise ValueError(f'{method} {path}: expected HTTP {expected}, got HTTP {response.status_code}.')
        payload = response.json()
        if path in ('/health', '/api/health/db') and payload.get('status') != 'ok':
            raise ValueError(f'{path}: service is not ready.')
        print(f'PASS: {method} {path} (HTTP {expected})')
        return payload

    for path in PUBLIC_PATHS:
        check('GET', path)
    for path in PROTECTED_PATHS:
        check('GET', path, 401)

    preflight = client.options('/api/auth/login', headers={
        'Origin': origin,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'authorization,content-type',
    })
    allowed_headers = {value.strip().lower() for value in preflight.headers.get('access-control-allow-headers', '').split(',')}
    if (preflight.status_code != 200
            or preflight.headers.get('access-control-allow-origin') != origin
            or 'POST' not in preflight.headers.get('access-control-allow-methods', '').split(', ')
            or not {'authorization', 'content-type'} <= allowed_headers):
        raise ValueError('CORS preflight failed for login/Bearer requests.')
    print('PASS: CORS preflight for login and Bearer requests')

    if not phone:
        print('SKIP: authenticated reads (set SMOKE_PHONE and SMOKE_PASSWORD).')
        return
    result = check('POST', '/api/auth/login', json={'phone': phone, 'password': password})
    headers = {'Authorization': f'Bearer {result["access_token"]}'}
    me = check('GET', '/api/auth/me', headers=headers)['user']
    if me != result['user']:
        raise ValueError('Login user and /api/auth/me do not match.')
    role = me['role']
    paths = STAFF_PATHS if role == 'staff' else MANAGER_PATHS
    for path in paths:
        check('GET', path, headers=headers)
    if role == 'admin':
        check('GET', '/api/query-explorer', headers=headers)
    elif role == 'staff':
        check('GET', '/api/employees', 403, headers=headers)
        check('GET', '/api/analytics/sales', 403, headers=headers)
    else:
        check('GET', '/api/query-explorer', 403, headers=headers)
        check('GET', '/api/customers', 403, headers=headers)
    print(f'PASS: authenticated read flow for {role}; no business data written.')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8000')
    parser.add_argument('--origin', default='http://127.0.0.1:8080')
    parser.add_argument('--login', action='store_true', help='Require SMOKE_PHONE and SMOKE_PASSWORD from the environment.')
    args = parser.parse_args()
    try:
        phone = os.getenv('SMOKE_PHONE', '') if args.login else ''
        password = os.getenv('SMOKE_PASSWORD', '') if args.login else ''
        if args.login and not (phone and password):
            raise ValueError('--login requires SMOKE_PHONE and SMOKE_PASSWORD environment variables.')
        with httpx.Client(base_url=args.url.rstrip('/'), timeout=90) as client:
            verify_api(client, args.origin, phone, password)
    except (httpx.HTTPError, ValueError, KeyError) as exc:
        print(f'FAIL: {exc}')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

import functools
import subprocess
import threading
from http.server import ThreadingHTTPServer
from unittest.mock import Mock

import httpx
import pytest

from scripts.dev import FrontendHandler, wait_for_api
from scripts.smoke_api import MANAGER_PATHS, PROTECTED_PATHS, PUBLIC_PATHS, STAFF_PATHS, verify_api


def test_dev_serves_custom_api_port_without_overwriting_deploy_config(tmp_path):
    config = tmp_path / 'config.js'
    config.write_text('window.FASHION_MANAGER_API_URL = "https://deployment.example";')
    previous = config.read_bytes()
    handler = functools.partial(FrontendHandler, directory=str(tmp_path), api_url='http://127.0.0.1:8010')
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        with httpx.Client(base_url=f'http://127.0.0.1:{server.server_port}', trust_env=False) as client:
            get = client.get('/config.js?cache=1')
            head = client.head('/config.js')
        assert get.status_code == head.status_code == 200
        assert 'http://127.0.0.1:8010' in get.text
        assert head.content == b''
        assert head.headers['content-length'] == str(len(get.content))
        assert get.headers['cache-control'] == 'no-store'
        assert config.read_bytes() == previous
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)


def test_dev_detects_backend_startup_failure():
    process = Mock(spec=subprocess.Popen)
    process.poll.return_value = 1
    with pytest.raises(RuntimeError, match='exited during startup'):
        wait_for_api(process, 'http://127.0.0.1:1')


def smoke_client(role='admin', failed_path=None, invalid_preflight=False):
    calls = []
    user = {'role': role, 'employee_id': 'NV_TEST'}
    origin = 'http://127.0.0.1:8080'

    def response(request):
        path = request.url.path
        calls.append((request.method, path))
        headers = {'Access-Control-Allow-Origin': origin}
        if request.method == 'OPTIONS':
            headers.update({
                'Access-Control-Allow-Headers': 'authorization, content-type',
                'Access-Control-Allow-Methods': 'GET, POST',
            })
            return httpx.Response(400 if invalid_preflight else 200, headers=headers)
        if path == failed_path:
            return httpx.Response(503, json={'detail': 'Unavailable'}, headers=headers)
        if path in {p.split('?')[0] for p in PUBLIC_PATHS}:
            return httpx.Response(200, json={'status': 'ok', 'items': []}, headers=headers)
        if path == '/api/auth/login':
            return httpx.Response(200, json={'access_token': 'test-token', 'user': user}, headers=headers)
        if path in PROTECTED_PATHS:
            if request.headers.get('Authorization') != 'Bearer test-token':
                return httpx.Response(401, json={'detail': 'Login required'}, headers=headers)
            if path == '/api/auth/me':
                return httpx.Response(200, json={'user': user}, headers=headers)
            allowed = STAFF_PATHS if role == 'staff' else MANAGER_PATHS
            status = 200 if path in allowed or (role == 'admin' and path == '/api/query-explorer') else 403
            return httpx.Response(status, json={'items': []}, headers=headers)
        raise AssertionError(f'Unexpected smoke request: {request.method} {path}')

    return httpx.Client(base_url='http://api.test', transport=httpx.MockTransport(response)), calls, origin


@pytest.mark.parametrize('role', ['admin', 'regional_manager', 'store_manager', 'staff'])
def test_authenticated_smoke_checks_roles_without_writing_business_data(role):
    client, calls, origin = smoke_client(role)
    with client:
        verify_api(client, origin, '0900000000', 'NV_TEST')
    assert ('GET', '/api/auth/me') in calls
    assert [(method, path) for method, path in calls if method == 'POST'] == [('POST', '/api/auth/login')]


def test_smoke_does_not_treat_database_failure_as_success():
    client, _, origin = smoke_client(failed_path='/api/health/db')
    with client, pytest.raises(ValueError, match='got HTTP 503'):
        verify_api(client, origin)


def test_smoke_rejects_broken_preflight_even_when_get_cors_works():
    client, _, origin = smoke_client(invalid_preflight=True)
    with client, pytest.raises(ValueError, match='preflight failed'):
        verify_api(client, origin)

from dataclasses import replace
from contextlib import contextmanager
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from mysql.connector import OperationalError

import app.db.connection as database
from app.core.config import database_address
from main import app
from scripts.build_frontend_config import build_config


def test_database_health_reports_schema_version_without_response_error(monkeypatch):
    import main
    cursor=MagicMock()
    cursor.fetchone.return_value=('8.0.45',)
    cursor.fetchall.return_value=[(3,)]
    conn=MagicMock()
    conn.cursor.return_value=cursor

    @contextmanager
    def connected():
        yield conn

    monkeypatch.setattr(main,'connection',connected)
    with TestClient(app) as client:
        response=client.get('/api/health/db')
    assert response.status_code==200,response.text
    assert response.json()=={'status':'ok','mysql_version':'8.0.45','schema_version':3}


def test_default_cors_allows_the_deployed_frontend(monkeypatch):
    from app.core.config import Settings
    monkeypatch.delenv('APP_CORS_ORIGINS', raising=False)
    origins = Settings().app_cors_origins
    assert 'https://thanhtech.cloud' in origins
    assert 'http://127.0.0.1:5500' in origins
    assert 'http://localhost:5500' in origins


def test_configured_cors_keeps_local_live_server_origins(monkeypatch):
    from app.core.config import Settings

    monkeypatch.setenv('APP_CORS_ORIGINS', 'https://preview.example.test')
    origins = Settings().app_cors_origins

    assert 'https://preview.example.test' in origins
    assert 'http://127.0.0.1:5500' in origins
    assert 'http://localhost:5500' in origins


@pytest.mark.parametrize('url', ['', 'http://api.example.com', 'https://localhost', 'https://127.0.0.1', 'https://api.example.com?password=secret', 'https://user:pass@api.example.com'])
def test_pages_rejects_invalid_or_private_backend(url):
    with pytest.raises(ValueError):
        build_config(url)


def test_pages_generates_valid_javascript():
    import json
    result = build_config(' https://api.example.com/ ')
    assert result.endswith(';\n')
    assert json.loads(result.split(' = ', 1)[1][:-2]) == 'https://api.example.com'


@pytest.mark.parametrize('host', [' mysql://db.example.com:15000/defaultdb ', '"db.example.com"', 'db.example.com:15000'])
def test_database_normalizes_host(host, monkeypatch):
    monkeypatch.setenv('DB_HOST', host)
    monkeypatch.setenv('DB_PORT', '15000')
    assert database_address() == ('db.example.com', 15000)


def test_remote_database_requires_tls(monkeypatch):
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = ('Ssl_cipher', '')
    monkeypatch.setattr(database, 'settings', replace(database.settings, db_host='db.example.com'))
    monkeypatch.setattr(database.mysql.connector, 'connect', lambda **kwargs: conn)
    with pytest.raises(database.mysql.connector.InterfaceError):
        with database.connection():
            pytest.fail('Unencrypted remote connection must not reach the application')
    conn.close.assert_called_once()


def test_aiven_certificate_and_hostname_are_verified(monkeypatch):
    conn = MagicMock()
    conn.cursor.return_value.fetchone.return_value = ('Ssl_cipher', 'TLS_AES_256_GCM_SHA384')
    connect = MagicMock(return_value=conn)
    monkeypatch.setattr(database, 'settings', replace(database.settings, db_host='db.example.com', db_ssl_ca='/secrets/ca.pem'))
    monkeypatch.setattr(database.mysql.connector, 'connect', connect)
    with database.connection() as actual:
        assert actual is conn
    assert connect.call_args.kwargs['ssl_verify_cert'] is True
    assert connect.call_args.kwargs['ssl_verify_identity'] is True
    assert connect.call_args.kwargs['ssl_ca'] == '/secrets/ca.pem'


def test_database_failure_returns_error_without_fake_products(monkeypatch):
    import main
    import app.routers.catalog as catalog

    def unavailable(*args, **kwargs):
        raise OperationalError('sensitive database connection details')

    monkeypatch.setattr(main, 'connection', unavailable)
    monkeypatch.setattr(catalog, 'list_products', unavailable)
    from app.core.authentication import get_current_user
    app.dependency_overrides[get_current_user] = lambda: {'assignments':[{'permissions':['catalog.read'],'pham_vi':'system'}]}
    with TestClient(app) as client:
        assert client.get('/').json()['service'] == 'Fashion Manager API'
        assert client.head('/').status_code == 200
        assert client.get('/health').json() == {'status': 'ok'}
        for path in ('/api/health/db', '/api/products'):
            response = client.get(path)
            assert response.status_code == 503
            assert 'items' not in response.json()
            assert 'sensitive' not in response.text
    app.dependency_overrides.clear()

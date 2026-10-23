import io
import json

import pytest
from dotenv import dotenv_values

from scripts import connect_backend
from scripts.prepare_render_env import write_environment


def test_render_environment_preserves_password_special_characters(tmp_path):
    target = tmp_path / '.env.render'
    values = {'DB_PASSWORD': 'a#b c"d\\e$xyz', 'DB_USER': 'example'}
    write_environment(target, values)
    assert dict(dotenv_values(target, interpolate=False)) == values


def test_backend_connection_rejects_wrong_cors_before_updating_secrets(monkeypatch):
    def response(*args, **kwargs):
        stream = io.BytesIO(json.dumps({'status': 'ok'}).encode())
        stream.headers = {}
        return stream

    monkeypatch.setattr(connect_backend, 'urlopen', response)
    with pytest.raises(ValueError, match='CORS'):
        connect_backend.verify_api('https://api.example.com', 'https://thanhtech.cloud')


def test_backend_connection_checks_all_real_endpoints(monkeypatch):
    calls = []

    def response(request, **kwargs):
        calls.append(request.full_url)
        stream = io.BytesIO(json.dumps({'status': 'ok', 'daily': []}).encode())
        stream.headers = {'Access-Control-Allow-Origin': 'https://thanhtech.cloud'}
        return stream

    monkeypatch.setattr(connect_backend, 'urlopen', response)
    connect_backend.verify_api('https://api.example.com', 'https://thanhtech.cloud')
    assert len(calls) == 7
    assert calls[-1].endswith('/api/analytics/sales')

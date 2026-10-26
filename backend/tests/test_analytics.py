from contextlib import contextmanager
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.routers.analytics import clean_referrer, device_type, masked_ip
from main import app


@pytest.mark.parametrize(('agent', 'expected'), [('iPhone Mobile', 'mobile'), ('Android Mobile', 'mobile'), ('iPad', 'tablet'), ('Android Tablet', 'tablet'), ('Windows NT', 'desktop')])
def test_device_classification(agent, expected):
    assert device_type(agent) == expected


def test_analytics_does_not_store_full_ip_or_referrer_credentials():
    assert masked_ip('192.168.1.123') == '192.168.1.0/24'
    assert masked_ip('2001:db8:1234:5678::1') == '2001:db8:1234::/48'
    assert clean_referrer('https://user:password@example.com/path?token=private') == 'example.com'
    assert clean_referrer('javascript:alert(1)') == ''


def test_dashboard_uses_vietnam_day_boundaries_and_real_empty_counts(monkeypatch):
    import app.repositories.analytics as repository
    cursor = MagicMock()
    cursor.fetchall.side_effect = [[], [], [], []]
    conn = MagicMock()
    conn.cursor.return_value = cursor

    @contextmanager
    def connected():
        yield conn

    monkeypatch.setattr(repository, 'connection', connected)
    result = repository.get_visit_dashboard(datetime(2026, 10, 22, 18, tzinfo=timezone.utc))
    assert result['daily'][0]['date'] == '2026-09-24'
    assert result['daily'][-1]['date'] == '2026-10-23'
    assert len(result['hourly']) == 24
    assert result['total'] == 0
    assert result['visits'] == []
    assert cursor.execute.call_args_list[0].args[1] == {
        "start": datetime(2026, 9, 23, 17),
        "end": datetime(2026, 10, 23, 17),
    }


def test_visit_is_persisted_only_on_explicit_tracking_request(monkeypatch):
    import app.routers.analytics as router
    recorder = MagicMock()
    monkeypatch.setattr(router, 'record_visit', recorder)
    monkeypatch.setattr(router, 'get_visit_dashboard', lambda: {'total': 0})
    import app.core.authentication as authentication
    app.dependency_overrides[authentication.get_current_user] = lambda: {
        "quyen_han": "admin",
    }
    with TestClient(app) as client:
        assert client.get('/api/analytics/visits').status_code == 200
        recorder.assert_not_called()
        response = client.post('/api/analytics/visits', json={'path': '/Fashion-Manager/', 'referrer': 'https://example.com/?token=secret'}, headers={'User-Agent': 'iPhone Mobile'})
        assert response.status_code == 201
        assert recorder.call_args.args[0] == '/Fashion-Manager/'
        assert recorder.call_args.args[2:] == ('mobile', 'example.com')
        assert client.post('/api/analytics/visits', json={'path': 'https://bad.example'}).status_code == 422
    app.dependency_overrides.clear()

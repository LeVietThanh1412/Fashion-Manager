from contextlib import contextmanager
from datetime import datetime, timezone
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from mysql.connector import OperationalError

from main import app


def test_sales_buckets_and_recent_orders_use_business_records(monkeypatch):
    import app.repositories.sales as repository
    cursor = MagicMock()
    cursor.fetchall.side_effect = [
        [{'day': '2026-10-23', 'count': 2, 'revenue': 350000}],
        [{'hour': 8, 'count': 2}],
        [{'id': 'DM01', 'name': 'Áo', 'count': 3}],
        [{'ma_don_hang': 'DH01', 'ngay_tao_don': datetime(2026, 10, 23, 8), 'ma_khach_hang': 'KH01', 'ten_cua_hang': 'Cửa hàng 1', 'quantity': 2, 'revenue': 150000}],
    ]
    conn = MagicMock()
    conn.cursor.return_value = cursor

    @contextmanager
    def connected():
        yield conn

    monkeypatch.setattr(repository, 'connection', connected)
    result = repository.get_sales_dashboard(datetime(2026, 10, 23, 2, tzinfo=timezone.utc))
    assert result['total_orders'] == 2
    assert result['total_revenue'] == 350000
    assert len(result['daily']) == 30
    assert result['daily'][-1]['count'] == 2
    assert result['daily'][0]['count'] == 0
    assert result['hourly'][8]['count'] == 2
    assert result['orders'][0]['timestamp'].endswith('+07:00')
    assert result['categories'][0]['count'] == 3
    assert cursor.execute.call_args_list[0].args[1] == (datetime(2026, 9, 24), datetime(2026, 10, 24))


def test_sales_failure_is_not_reported_as_zero_revenue(monkeypatch):
    import app.routers.analytics as router

    def unavailable():
        raise OperationalError('private database details')

    monkeypatch.setattr(router, 'get_sales_dashboard', unavailable)
    with TestClient(app) as client:
        response = client.get('/api/analytics/sales')
        assert response.status_code == 503
        assert 'total_revenue' not in response.json()
        assert 'private database' not in response.text

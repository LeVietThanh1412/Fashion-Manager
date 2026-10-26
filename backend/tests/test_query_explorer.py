from contextlib import contextmanager
from unittest.mock import MagicMock

from app.db.academic_queries import AcademicQuery
from app.routers import query_explorer


def test_execute_query_returns_column_names_even_without_rows(monkeypatch):
    cursor = MagicMock()
    cursor.description = (("ma_nhan_vien",), ("ho_ten",))
    cursor.fetchmany.return_value = []
    connection = MagicMock()
    connection.cursor.return_value = cursor

    @contextmanager
    def connected():
        yield connection

    monkeypatch.setattr(query_explorer, "connection", connected)
    monkeypatch.setitem(
        query_explorer.QUERIES,
        "M02_Q01",
        AcademicQuery("M02_Q01", "Nhan vien va cua hang 1", "SELECT 1;"),
    )

    result = query_explorer.execute_query("M02_Q01", _admin={})

    assert result == {
        "query_id": "M02_Q01",
        "columns": ["ma_nhan_vien", "ho_ten"],
        "items": [],
    }
    cursor.execute.assert_called_once_with("SELECT 1;")
    cursor.fetchmany.assert_called_once_with(500)

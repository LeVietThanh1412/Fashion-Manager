from contextlib import contextmanager
from unittest.mock import MagicMock

from app.routers import query_explorer


def test_list_queries_picks_up_queries_added_after_module_load(tmp_path, monkeypatch):
    query_file = tmp_path / "member_01.sql"
    query_file.write_text("-- 1. Truy vấn đầu tiên\nSELECT 1;", encoding="utf-8")
    monkeypatch.setattr(query_explorer, "QUERY_ROOT", tmp_path)

    first_result = query_explorer.list_queries(_admin={})
    query_file.write_text(
        "-- 1. Truy vấn đầu tiên\nSELECT 1;\n\n-- 2. Truy vấn mới\nSELECT 2;",
        encoding="utf-8",
    )
    second_result = query_explorer.list_queries(_admin={})

    assert first_result["items"] == [{"query_id": "M01_Q01", "title": "Truy vấn đầu tiên"}]
    assert second_result["items"] == [
        {"query_id": "M01_Q01", "title": "Truy vấn đầu tiên"},
        {"query_id": "M01_Q02", "title": "Truy vấn mới"},
    ]


def test_execute_query_returns_column_names_even_without_rows(tmp_path, monkeypatch):
    cursor = MagicMock()
    cursor.description = (("ma_nhan_vien",), ("ho_ten",))
    cursor.fetchmany.return_value = []
    connection = MagicMock()
    connection.cursor.return_value = cursor

    @contextmanager
    def connected():
        yield connection

    query_root = tmp_path / "queries"
    query_root.mkdir()
    (query_root / "member_02.sql").write_text(
        "-- Query ID: M02_Q01\n-- Title: Nhan vien va cua hang 1\nSELECT 1;",
        encoding="utf-8",
    )
    monkeypatch.setattr(query_explorer, "QUERY_ROOT", query_root)
    monkeypatch.setattr(query_explorer, "connection", connected)

    result = query_explorer.execute_query("M02_Q01", _admin={})

    assert result == {
        "query_id": "M02_Q01",
        "columns": ["ma_nhan_vien", "ho_ten"],
        "items": [],
    }
    cursor.execute.assert_called_once_with("SELECT 1;")
    cursor.fetchmany.assert_called_once_with(500)

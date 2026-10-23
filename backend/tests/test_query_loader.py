from pathlib import Path

import pytest

from app.db.academic_queries import load_academic_queries
from app.db.query_loader import QueryLoadError, QueryLoader


def test_loader_reads_sql() -> None:
    loader = QueryLoader(Path(__file__).parents[2] / "sql" / "app")
    assert "SELECT" in loader.load("products/get_by_id.sql")


def test_loader_rejects_traversal() -> None:
    loader = QueryLoader(Path(__file__).parents[2] / "sql" / "app")
    with pytest.raises(QueryLoadError):
        loader.load("../schema/02_create_tables.sql")


def test_loader_rejects_non_sql() -> None:
    loader = QueryLoader(Path(__file__).parents[2] / "sql" / "app")
    with pytest.raises(QueryLoadError):
        loader.load("products/get_by_id.txt")


def test_academic_registry_contains_50_read_only_queries() -> None:
    root = Path(__file__).parents[2] / "sql" / "query"
    queries = load_academic_queries(root)
    assert len(queries) == 50
    assert all(query.sql.upper().startswith("SELECT ") for query in queries.values())

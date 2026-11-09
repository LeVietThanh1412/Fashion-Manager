from pathlib import Path
import re

import pytest

from app.db.academic_queries import load_academic_queries
from app.db.query_loader import QueryLoadError, QueryLoader


def test_loader_reads_sql() -> None:
    loader = QueryLoader(Path(__file__).parents[2] / "sql" / "app")
    assert "SELECT" in loader.load("auth/by_phone.sql")


def test_loader_rejects_traversal() -> None:
    loader = QueryLoader(Path(__file__).parents[2] / "sql" / "app")
    with pytest.raises(QueryLoadError):
        loader.load("../data/01_create_database.sql")


def test_loader_rejects_non_sql() -> None:
    loader = QueryLoader(Path(__file__).parents[2] / "sql" / "app")
    with pytest.raises(QueryLoadError):
        loader.load("auth/by_phone.txt")


def test_academic_registry_contains_all_numbered_and_registered_queries() -> None:
    root = Path(__file__).parents[2] / "sql" / "query"
    queries = load_academic_queries(root)
    assert len(queries) == 77
    for member_number in range(1, 6):
        member_queries = [
            query for query in queries.values()
            if query.query_id.startswith(f"M{member_number:02d}_")
        ]
        expected = 17 if member_number == 3 else 15
        assert len(member_queries) == expected
        assert [query.query_id for query in member_queries] == [
            f"M{member_number:02d}_Q{query_number:02d}" for query_number in range(1, expected + 1)
        ]
    assert all(re.match(r"(?i)^(SELECT|WITH)\b", query.sql.lstrip()) for query in queries.values())

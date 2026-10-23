from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from app.db.academic_queries import AcademicQuery, load_academic_queries
from app.db.connection import connection

QUERY_ROOT = Path(__file__).resolve().parents[3] / "sql" / "query"
QUERIES = load_academic_queries(QUERY_ROOT)
router = APIRouter(prefix="/api/query-explorer", tags=["query-explorer"])


@router.get("")
def list_queries() -> dict[str, list[dict[str, str]]]:
    return {
        "items": [
            {"query_id": query.query_id, "title": query.title}
            for query in sorted(QUERIES.values(), key=lambda item: item.query_id)
        ]
    }


@router.post("/{query_id}")
def execute_query(query_id: str) -> dict[str, Any]:
    query: AcademicQuery | None = QUERIES.get(query_id)
    if query is None:
        raise HTTPException(status_code=404, detail="Unknown query ID")
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query.sql)
            return {"query_id": query_id, "items": list(cursor.fetchmany(500))}
        finally:
            cursor.close()

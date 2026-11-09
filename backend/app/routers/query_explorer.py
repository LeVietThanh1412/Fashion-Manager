from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.db.academic_queries import AcademicQuery, adapt_query_to_current_schema, load_academic_queries
from app.db.connection import connection
from app.core.authentication import require_permissions

QUERY_ROOT = Path(__file__).resolve().parents[3] / "sql" / "query"
router = APIRouter(prefix="/api/query-explorer", tags=["query-explorer"])


@router.get("")
def list_queries(_admin: dict = Depends(require_permissions("queries.execute", system=True))) -> dict[str, list[dict[str, str]]]:
    queries = load_academic_queries(QUERY_ROOT)
    return {
        "items": [
            {"query_id": query.query_id, "title": query.title}
            for query in sorted(queries.values(), key=lambda item: item.query_id)
        ]
    }


@router.post("/{query_id}")
def execute_query(query_id: str, _admin: dict = Depends(require_permissions("queries.execute", system=True))) -> dict[str, Any]:
    queries = load_academic_queries(QUERY_ROOT)
    query: AcademicQuery | None = queries.get(query_id)
    if query is None:
        raise HTTPException(status_code=404, detail="Unknown query ID")
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            statement, notice = adapt_query_to_current_schema(query)
            cursor.execute(statement)
            columns = [column[0] for column in cursor.description or ()]
            result = {
                "query_id": query_id,
                "columns": columns,
                "items": list(cursor.fetchmany(500)),
            }
            if notice:
                result["notice"] = notice
            return result
        finally:
            cursor.close()

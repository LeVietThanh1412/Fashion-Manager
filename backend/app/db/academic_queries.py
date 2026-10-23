from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class AcademicQuery:
    query_id: str
    title: str
    sql: str


_ID_RE = re.compile(r"-- Query ID: (M\d{2}_Q\d{2})\r?\n")
_TITLE_RE = re.compile(r"-- Title: (.+)\r?\n")


def load_academic_queries(root: Path) -> dict[str, AcademicQuery]:
    registry: dict[str, AcademicQuery] = {}
    for path in sorted(root.glob("member_*.sql")):
        text = path.read_text(encoding="utf-8")
        matches = list(_ID_RE.finditer(text))
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            block = text[match.start():end]
            title_match = _TITLE_RE.search(block)
            statement = block[block.find("SELECT "):].strip()
            if not title_match or not statement.endswith(";"):
                raise ValueError(f"Invalid academic query block in {path.name}")
            query = AcademicQuery(match.group(1), title_match.group(1), statement)
            if query.query_id in registry:
                raise ValueError(f"Duplicate academic query ID: {query.query_id}")
            if not statement.upper().startswith("SELECT "):
                raise ValueError(f"Academic query is not read-only: {query.query_id}")
            registry[query.query_id] = query
    return registry

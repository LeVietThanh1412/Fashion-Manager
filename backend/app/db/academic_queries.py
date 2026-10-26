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
_NUMBERED_QUERY_RE = re.compile(r"(?m)^--\s+(\d{1,2})\.\s+(.+?)\r?$")
_SQL_START_RE = re.compile(r"(?im)^\s*(SELECT|WITH)\b")
_SQL_COMMENT_RE = re.compile(r"--[^\r\n]*|/\*.*?\*/", re.DOTALL)
_NON_READ_ONLY_RE = re.compile(
    r"\b(INSERT|UPDATE|DELETE|REPLACE|CREATE|ALTER|DROP|TRUNCATE|GRANT|REVOKE|CALL|LOAD)\b"
    r"|\bFOR\s+UPDATE\b|\bINTO\s+(OUTFILE|DUMPFILE)\b",
    re.IGNORECASE,
)


def _is_read_only(statement: str) -> bool:
    sql = _SQL_COMMENT_RE.sub("", statement).strip()
    if not _SQL_START_RE.match(sql) or _NON_READ_ONLY_RE.search(sql):
        return False
    semicolons = [index for index, character in enumerate(sql) if character == ";"]
    return len(semicolons) <= 1 and (not semicolons or semicolons[0] == len(sql) - 1)


def _load_numbered_queries(path: Path) -> list[AcademicQuery]:
    text = path.read_text(encoding="utf-8")
    matches = list(_NUMBERED_QUERY_RE.finditer(text))
    queries = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[match.end():end]
        sql_start = _SQL_START_RE.search(section)
        if not sql_start:
            raise ValueError(f"Missing SQL statement for query {match.group(1)} in {path.name}")
        lines = []
        for line in section[sql_start.start():].splitlines():
            if line.lstrip().startswith("--"):
                break
            lines.append(line)
        statement = "\n".join(lines).strip()
        if not statement.endswith(";"):
            statement += ";"
        if not _is_read_only(statement):
            raise ValueError(f"Academic query is not read-only: M01_Q{int(match.group(1)):02d}")
        query_id = f"M01_Q{int(match.group(1)):02d}"
        queries.append(AcademicQuery(query_id, match.group(2).strip(), statement))
    return queries


def adapt_query_to_current_schema(query: AcademicQuery) -> tuple[str, str | None]:
    statement = re.sub(r"\bgia_ban\b", "gia_san_pham", query.sql, flags=re.IGNORECASE)
    notice = None

    if query.query_id.startswith("M04_") and re.search(r"\bct\.don_gia_ban\b", statement, re.IGNORECASE):
        join_pattern = re.compile(
            r"(JOIN\s+chi_tiet_don_hang\s+ct\s+ON\s+ct\.ma_don_hang\s*=\s*d\.ma_don_hang)",
            re.IGNORECASE,
        )
        statement, join_count = join_pattern.subn(
            r"\1 JOIN san_pham sp ON sp.ma_san_pham = ct.ma_san_pham",
            statement,
            count=1,
        )
        if not join_count:
            raise ValueError(f"Cannot adapt current-schema price for {query.query_id}")
        statement = re.sub(
            r"\bct\.don_gia_ban\b",
            "sp.gia_san_pham",
            statement,
            flags=re.IGNORECASE,
        )
        notice = "Đơn giá lịch sử không có trong schema; dùng giá sản phẩm hiện tại."
    elif query.query_id == "M05_Q09":
        statement, count = re.subn(
            r"AVG\s*\(\s*don_gia_ban\s*\)\s+AS\s+gia_ban_trung_binh\s+FROM\s+chi_tiet_don_hang",
            "AVG(sp.gia_san_pham) AS gia_ban_trung_binh "
            "FROM chi_tiet_don_hang AS ct "
            "JOIN san_pham AS sp ON sp.ma_san_pham = ct.ma_san_pham",
            statement,
            flags=re.IGNORECASE,
        )
        if not count:
            raise ValueError(f"Cannot adapt current-schema price for {query.query_id}")
        notice = "Đơn giá lịch sử không có trong schema; dùng giá sản phẩm hiện tại."
    elif re.search(r"\bdon_gia_ban\b", statement, re.IGNORECASE):
        raise ValueError(f"Unsupported price column in {query.query_id}")

    statement = re.sub(r"\bct\.ma_chi_tiet\b", "ct.ma_san_pham", statement, flags=re.IGNORECASE)
    return statement, notice


def load_academic_queries(root: Path) -> dict[str, AcademicQuery]:
    registry: dict[str, AcademicQuery] = {}
    for path in sorted(root.glob("member_*.sql")):
        if path.name == "member_01.sql":
            for query in _load_numbered_queries(path):
                if query.query_id in registry:
                    raise ValueError(f"Duplicate academic query ID: {query.query_id}")
                registry[query.query_id] = query
            continue
        text = path.read_text(encoding="utf-8")
        matches = list(_ID_RE.finditer(text))
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            block = text[match.start():end]
            title_match = _TITLE_RE.search(block)
            sql_start = _SQL_START_RE.search(block)
            if not title_match or not sql_start:
                raise ValueError(f"Invalid academic query block in {path.name}")
            statement = block[sql_start.start():].strip()
            query = AcademicQuery(match.group(1), title_match.group(1), statement)
            if query.query_id in registry:
                raise ValueError(f"Duplicate academic query ID: {query.query_id}")
            if not _is_read_only(statement):
                raise ValueError(f"Academic query is not read-only: {query.query_id}")
            registry[query.query_id] = query
    return registry

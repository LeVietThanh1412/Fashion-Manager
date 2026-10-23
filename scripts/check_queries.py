"""Static checks for the academic query set; no database connection required."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
QUERY_DIR = ROOT / "sql" / "query"
ID_RE = re.compile(r"-- Query ID: (M\d{2}_Q\d{2})")


def main() -> int:
    files = sorted(QUERY_DIR.glob("member_*.sql"))
    errors: list[str] = []
    ids: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        found = ID_RE.findall(text)
        if len(found) < 10:
            errors.append(f"{path.name}: expected at least 10 IDs, got {len(found)}")
        if text.upper().count("SELECT ") < 10:
            errors.append(f"{path.name}: expected at least 10 SELECT statements")
        ids.extend(found)
    if len(files) != 5:
        errors.append(f"expected exactly 5 member files, got {len(files)}")
    if len(ids) < 50 or len(set(ids)) != len(ids):
        errors.append("expected at least 50 unique query IDs")
    required = ("COUNT", "SUM", "AVG", "MIN", "MAX", "UNION", "INTERSECT", "EXCEPT")
    all_text = "\n".join(p.read_text(encoding="utf-8").upper() for p in files)
    for keyword in required:
        if keyword not in all_text:
            errors.append(f"missing required feature: {keyword}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"PASS: {len(files)} files, {len(ids)} unique query IDs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

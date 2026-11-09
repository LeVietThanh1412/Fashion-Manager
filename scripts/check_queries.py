"""Static checks for the academic query set; no database connection required."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
QUERY_DIR = ROOT / "sql" / "query"
NUMBERED_RE = re.compile(r"(?m)^[ \t]*--\s+(\d{1,2})\.\s+")


def main() -> int:
    files = sorted(QUERY_DIR.glob("member_*.sql"))
    errors: list[str] = []
    ids: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        member_match = re.fullmatch(r"member_(\d{2})\.sql", path.name)
        if not member_match:
            errors.append(f"{path.name}: invalid member file name")
            continue
        headings = list(NUMBERED_RE.finditer(text))
        found = [f"M{member_match.group(1)}_Q{int(match.group(1)):02d}" for match in headings]
        expected = 17 if member_match.group(1) == "03" else 15
        if len(found) != expected:
            errors.append(f"{path.name}: expected {expected} numbered queries, got {len(found)}")
        if [int(query_id[-2:]) for query_id in found] != list(range(1, expected + 1)):
            errors.append(f"{path.name}: expected query titles numbered 1 through {expected} in order")
        for index, heading in enumerate(headings):
            end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
            if not re.search(r"(?im)^[ \t]*(SELECT|WITH)\b", text[heading.end():end]):
                errors.append(f"{path.name}: query {found[index][-2:]} is missing its SELECT/WITH statement")
        ids.extend(found)
    if len(files) != 5:
        errors.append(f"expected exactly 5 member files, got {len(files)}")
    if len(ids) != 77 or len(set(ids)) != len(ids):
        errors.append("expected exactly 77 unique query IDs")
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

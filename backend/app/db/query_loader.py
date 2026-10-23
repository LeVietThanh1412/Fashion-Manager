from pathlib import Path
from functools import lru_cache


class QueryLoadError(ValueError):
    """Raised when a registered SQL file cannot be loaded safely."""


class QueryLoader:
    def __init__(self, root: Path):
        self.root = root.resolve()

    @lru_cache(maxsize=128)
    def load(self, relative_path: str) -> str:
        candidate = (self.root / relative_path).resolve()
        if candidate.parent != self.root and self.root not in candidate.parents:
            raise QueryLoadError("SQL path escapes the configured root")
        if candidate.suffix.lower() != ".sql":
            raise QueryLoadError("Only .sql files can be loaded")
        if not candidate.is_file():
            raise QueryLoadError(f"SQL file not found: {relative_path}")
        text = candidate.read_text(encoding="utf-8").strip()
        if not text:
            raise QueryLoadError(f"SQL file is empty: {relative_path}")
        return text

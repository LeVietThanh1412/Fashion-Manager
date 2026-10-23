"""Create only the web analytics table; never reset or seed business data."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))

from app.db.connection import connection


def main() -> None:
    with connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute((ROOT / 'sql/migrations/03_web_analytics.sql').read_text(encoding='utf-8'))
            conn.commit()
        finally:
            cursor.close()
    print('PASS: web analytics table is ready. Existing data preserved; no visits seeded.')


if __name__ == '__main__':
    main()

"""Prepare an ignored Render environment file from the verified local Aiven settings."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))

from app.core.config import settings
from app.db.connection import connection


def write_environment(destination: Path, values: dict[str, str]) -> None:
    destination.write_text('\n'.join(f'{name}={json.dumps(value, ensure_ascii=False)}' for name, value in values.items()) + '\n', encoding='utf-8')


def main() -> None:
    with connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT 1')
            assert cursor.fetchone()[0] == 1
        finally:
            cursor.close()
    write_environment(ROOT / '.env.render', {
        'PYTHON_VERSION': '3.12.13',
        'DB_HOST': settings.db_host, 'DB_PORT': str(settings.db_port),
        'DB_NAME': settings.db_name, 'DB_USER': settings.db_user, 'DB_PASSWORD': settings.db_password,
        'APP_CORS_ORIGINS': 'https://thanhtech.cloud,https://levietthanh1412.github.io',
    })
    print('PASS: Aiven verified. Created .env.render for Render Import .env; credentials are not printed.')


if __name__ == '__main__':
    main()

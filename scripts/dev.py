"""Run API + static frontend together against the database in .env."""
import functools
import json
import os
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    if sys.version_info < (3, 10):
        raise SystemExit('Python 3.10+ required; use Python 3.12 or 3.13.')
    if not (ROOT / '.env').exists():
        raise SystemExit('Create .env from .env.example and enter your Aiven connection settings first.')
    config = ROOT / 'frontend' / 'config.js'
    previous = config.read_bytes() if config.exists() else None
    server = ThreadingHTTPServer(('127.0.0.1', 8080), functools.partial(SimpleHTTPRequestHandler, directory=str(ROOT / 'frontend')))
    process = None
    try:
        environment = os.environ.copy()
        origins = environment.get('APP_CORS_ORIGINS', dotenv_values(ROOT / '.env').get('APP_CORS_ORIGINS') or '')
        environment['APP_CORS_ORIGINS'] = origins + ',http://localhost:8080,http://127.0.0.1:8080'
        config.write_text('window.FASHION_MANAGER_API_URL = ' + json.dumps('http://127.0.0.1:8000') + ';\n', encoding='utf-8')
        process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 'main:app', '--app-dir', 'backend',
            '--host', '127.0.0.1', '--port', '8000',
        ], cwd=ROOT, env=environment)
        print('Frontend: http://127.0.0.1:8080 | API docs: http://127.0.0.1:8000/docs', flush=True)
        print('Press Ctrl+C to stop both servers.', flush=True)
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        if process is not None:
            process.terminate()
            process.wait(timeout=10)
        if previous is None:
            config.unlink(missing_ok=True)
        else:
            config.write_bytes(previous)


if __name__ == '__main__':
    main()

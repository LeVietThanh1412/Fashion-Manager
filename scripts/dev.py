"""Run API + static frontend together against the database in .env."""
import functools
import argparse
import json
import os
import subprocess
import socket
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--api-port', type=int, default=8000)
    parser.add_argument('--frontend-port', type=int, default=8080)
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        raise SystemExit('Python 3.10+ required; use Python 3.12 or 3.13.')
    if not (ROOT / '.env').exists():
        raise SystemExit('Create .env from .env.example and enter your Aiven connection settings first.')
    config = ROOT / 'frontend' / 'config.js'
    previous = config.read_bytes() if config.exists() else None
    with socket.socket() as probe:
        try:
            probe.bind(('127.0.0.1', args.api_port))
        except OSError as exc:
            raise SystemExit('API port already in use; stop the old backend or pass --api-port 8010.') from exc
    server = ThreadingHTTPServer(('127.0.0.1', args.frontend_port), functools.partial(SimpleHTTPRequestHandler, directory=str(ROOT / 'frontend')))
    process = None
    try:
        environment = os.environ.copy()
        origins = environment.get('APP_CORS_ORIGINS', dotenv_values(ROOT / '.env').get('APP_CORS_ORIGINS') or '')
        environment['APP_CORS_ORIGINS'] = origins + f',http://localhost:{args.frontend_port},http://127.0.0.1:{args.frontend_port}'
        config.write_text('window.FASHION_MANAGER_API_URL = ' + json.dumps(f'http://127.0.0.1:{args.api_port}') + ';\n', encoding='utf-8')
        process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 'main:app', '--app-dir', 'backend',
            '--host', '127.0.0.1', '--port', str(args.api_port),
        ], cwd=ROOT, env=environment)
        print(f'Frontend: http://127.0.0.1:{args.frontend_port} | API docs: http://127.0.0.1:{args.api_port}/docs', flush=True)
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

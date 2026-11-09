"""Run API + static frontend together against the database in .env."""
import functools
import getpass
import io
import argparse
import json
import os
import subprocess
import socket
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import urlopen

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]


class FrontendHandler(SimpleHTTPRequestHandler):
    """Serve local config in memory; never overwrite the deployment config."""

    def __init__(self, *args, api_url: str, **kwargs):
        self.api_url = api_url
        super().__init__(*args, **kwargs)

    def send_head(self):
        if urlsplit(self.path).path == '/config.js':
            content = ('window.FASHION_MANAGER_API_URL = ' + json.dumps(self.api_url) + ';\n').encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/javascript; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            return io.BytesIO(content)
        return super().send_head()


def wait_for_api(process: subprocess.Popen, api_url: str, timeout: float = 20) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError('Backend exited during startup. See the API error above.')
        try:
            with urlopen(api_url + '/health', timeout=1) as response:
                if response.status == 200:
                    return
        except (URLError, TimeoutError, OSError):
            pass
        time.sleep(0.2)
    raise RuntimeError('Backend did not become ready within 20 seconds.')


def local_env_file() -> Path:
    return ROOT / '.env'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--api-port', type=int, default=8000)
    parser.add_argument('--frontend-port', type=int, default=8080)
    parser.add_argument('--config', type=Path, help='Explicit env file for this local run')
    args = parser.parse_args()
    if not all(1 <= port <= 65535 for port in (args.api_port, args.frontend_port)):
        parser.error('Ports must be between 1 and 65535.')
    if args.api_port == args.frontend_port:
        parser.error('API and frontend must use different ports.')
    if sys.version_info < (3, 10):
        raise SystemExit('Python 3.10+ required; use Python 3.12 or 3.13.')
    env_file = args.config or local_env_file()
    if not env_file.exists():
        raise SystemExit('Create a local config from .env.example or pass --config.')
    values = dotenv_values(env_file)
    secret = (values.get('AUTH_TOKEN_SECRET') or '') if args.config else os.environ.get('AUTH_TOKEN_SECRET', values.get('AUTH_TOKEN_SECRET') or '')
    if len(secret.encode('utf-8')) < 32:
        raise SystemExit(f'Set a private AUTH_TOKEN_SECRET of at least 32 bytes in {env_file} before starting the login API.')
    environment = os.environ.copy()
    if args.config:
        environment.update({key:value for key,value in values.items() if value is not None})
        if (values.get('APP_ENV') == 'development' and values.get('DB_HOST') in ('127.0.0.1','localhost','::1')):
            if not environment.get('DB_PASSWORD'):
                environment['DB_PASSWORD'] = getpass.getpass('Local MySQL password (hidden; type then Enter): ')
            import mysql.connector
            try:
                with mysql.connector.connect(
                    host=values['DB_HOST'],port=int(values['DB_PORT']),database=values['DB_NAME'],
                    user=values['DB_USER'],password=environment['DB_PASSWORD'],connection_timeout=5
                ) as database:
                    cursor=database.cursor()
                    cursor.execute('SELECT version FROM schema_version')
                    if cursor.fetchall()!=[(3,)]:
                        raise ValueError('The configured database does not have schema v3.')
                    cursor.close()
            except mysql.connector.Error as exc:
                raise SystemExit(f'Cannot access the configured local MySQL database (error {exc.errno}). Check the password and dev.local.env.') from None
            except ValueError as exc:
                raise SystemExit(str(exc)) from None
    api_url = f'http://127.0.0.1:{args.api_port}'
    with socket.socket() as probe:
        try:
            probe.bind(('127.0.0.1', args.api_port))
        except OSError as exc:
            raise SystemExit('API port already in use; stop the old backend or pass --api-port 8010.') from exc
    try:
        server = ThreadingHTTPServer(
            ('127.0.0.1', args.frontend_port),
            functools.partial(FrontendHandler, api_url=api_url, directory=str(ROOT / 'frontend')),
        )
    except OSError as exc:
        raise SystemExit('Frontend port already in use; stop the old frontend or pass --frontend-port 8081.') from exc
    process = None
    try:
        origins = environment.get('APP_CORS_ORIGINS', values.get('APP_CORS_ORIGINS') or '')
        environment['APP_CORS_ORIGINS'] = origins + (
            f',http://localhost:{args.frontend_port},http://127.0.0.1:{args.frontend_port}'
            ',http://localhost:5500,http://127.0.0.1:5500'
        )
        process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 'main:app', '--app-dir', 'backend',
            '--host', '127.0.0.1', '--port', str(args.api_port),
        ], cwd=ROOT, env=environment)
        wait_for_api(process, api_url)
        print(f'Frontend: http://127.0.0.1:{args.frontend_port} | API docs: http://127.0.0.1:{args.api_port}/docs', flush=True)
        print('Press Ctrl+C to stop both servers.', flush=True)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        while process.poll() is None:
            time.sleep(0.5)
        raise RuntimeError('Backend stopped. Restart scripts/dev.py after fixing the API error.')
    except KeyboardInterrupt:
        pass
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
    finally:
        if 'worker' in locals():
            server.shutdown()
            worker.join(timeout=5)
        server.server_close()
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


if __name__ == '__main__':
    main()

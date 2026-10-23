"""Validate a deployed API, update its GitHub Secret, then start frontend deployment."""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_frontend_config import build_config


def git_output(*args: str, input_text: str | None = None) -> str:
    environment = {**os.environ, 'GIT_TERMINAL_PROMPT': '0', 'GCM_INTERACTIVE': 'never'}
    result = subprocess.run(['git', *args], cwd=ROOT, input=input_text, text=True, capture_output=True, env=environment, timeout=30)
    if result.returncode:
        raise ValueError('Git credential unavailable. Authenticate Git for this repository, or set GH_TOKEN locally.')
    return result.stdout.strip()


def repository_name() -> str:
    remote = git_output('remote', 'get-url', 'origin')
    match = re.fullmatch(r'(?:https://github\.com/|git@github\.com:)([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?', remote)
    if not match:
        raise ValueError('origin must be a github.com repository URL.')
    return match.group(1)


def github_token() -> str:
    supplied = os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN')
    if supplied:
        return supplied
    output = git_output('credential', 'fill', input_text='protocol=https\nhost=github.com\n\n')
    credentials = dict(line.split('=', 1) for line in output.splitlines() if '=' in line)
    if not credentials.get('password'):
        raise ValueError('No GitHub token available from Git Credential Manager.')
    return credentials['password']


def github_request(token: str, path: str, method: str = 'GET', payload: dict | None = None):
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
    body = json.dumps(payload).encode() if payload is not None else None
    if body is not None:
        headers['Content-Type'] = 'application/json'
    try:
        with urlopen(Request('https://api.github.com' + path, headers=headers, data=body, method=method), timeout=30) as response:
            content = response.read()
            return json.loads(content) if content else None
    except HTTPError as exc:
        raise ValueError(f'GitHub {method} {path} failed with HTTP {exc.code}. Check repository permissions.') from None


def verify_api(url: str, origin: str) -> None:
    for path in ('/health', '/api/health/db', '/api/products', '/api/categories', '/api/stores', '/api/analytics/summary', '/api/analytics/visits'):
        try:
            with urlopen(Request(url + path, headers={'Origin': origin}), timeout=90) as response:
                data = json.load(response)
                if response.headers.get('Access-Control-Allow-Origin') != origin:
                    raise ValueError(f'Backend CORS must allow {origin}. Update APP_CORS_ORIGINS on Render.')
                if path in ('/health', '/api/health/db') and data.get('status') != 'ok':
                    raise ValueError(f'Backend {path} is not ready.')
                if path == '/api/analytics/visits' and 'daily' not in data:
                    raise ValueError('The deployed backend is missing web analytics.')
        except (HTTPError, URLError) as exc:
            raise ValueError(f'Backend {path} is unavailable ({type(exc).__name__}). Check Render deployment and database settings.') from None
        print(f'PASS: {path}')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('api_url', help='HTTPS URL shown on your deployed Render API service')
    args = parser.parse_args()
    # Reuse the same URL validation used by GitHub Actions, before any changes.
    config = build_config(args.api_url)
    url = json.loads(config.split(' = ', 1)[1][:-2])
    token = github_token()
    repo = repository_name()
    base = f'/repos/{repo}'
    pages = github_request(token, base + '/pages')
    page_url = urlsplit(pages['html_url'])
    origin = f'{page_url.scheme}://{page_url.netloc}'
    verify_api(url, origin)
    try:
        from nacl import public
    except ImportError:
        raise ValueError('Install setup dependency: python -m pip install PyNaCl') from None
    key = github_request(token, base + '/actions/secrets/public-key')
    box = public.SealedBox(public.PublicKey(base64.b64decode(key['key'])))
    encrypted = base64.b64encode(box.encrypt(url.encode())).decode()
    github_request(token, base + '/actions/secrets/FRONTEND_API_URL', 'PUT', {'encrypted_value': encrypted, 'key_id': key['key_id']})
    # Keep an existing public Variable consistent because the workflow prioritizes it.
    variables = github_request(token, base + '/actions/variables')
    if any(item['name'] == 'FRONTEND_API_URL' for item in variables['variables']):
        github_request(token, base + '/actions/variables/FRONTEND_API_URL', 'PATCH', {'name': 'FRONTEND_API_URL', 'value': url})
    if pages.get('build_type') != 'workflow':
        github_request(token, base + '/pages', 'PUT', {'build_type': 'workflow'})
    github_request(token, base + '/actions/workflows/deploy.yml/dispatches', 'POST', {'ref': 'main'})
    print(f'UPDATED: FRONTEND_API_URL. Deployment started: https://github.com/{repo}/actions')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, URLError) as exc:
        raise SystemExit(str(exc)) from None

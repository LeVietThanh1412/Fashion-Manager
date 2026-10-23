"""Generate the public Pages configuration. Never read database credentials."""
import ipaddress
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def build_config(api_url: str) -> str:
    url = api_url.strip().rstrip('/')
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname:
        raise ValueError('FRONTEND_API_URL must be the public HTTPS backend URL.')
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('FRONTEND_API_URL must not contain credentials, query parameters or a fragment.')
    hostname = parsed.hostname.lower()
    local = hostname == 'localhost' or hostname.endswith('.localhost')
    try:
        local = local or not ipaddress.ip_address(hostname).is_global
    except ValueError:
        pass
    if local:
        raise ValueError('FRONTEND_API_URL cannot point to localhost or a private IP on GitHub Pages.')
    return 'window.FASHION_MANAGER_API_URL = ' + json.dumps(url) + ';\n'


def main() -> None:
    try:
        config = build_config(os.getenv('FRONTEND_API_URL', ''))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    (ROOT / 'frontend' / 'config.js').write_text(config, encoding='utf-8')
    print('Generated frontend/config.js with the public HTTPS backend URL.')


if __name__ == '__main__':
    main()

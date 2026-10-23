"""Read-only smoke test of a running API, including optional frontend CORS origin."""
import argparse
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8000')
    parser.add_argument('--origin', default='http://127.0.0.1:8080')
    args = parser.parse_args()
    try:
        for path in ('/health', '/api/health/db', '/api/products?limit=100', '/api/categories', '/api/stores', '/api/analytics/summary', '/api/analytics/sales'):
            request = Request(args.url.rstrip('/') + path, headers={'Origin': args.origin})
            with urlopen(request, timeout=90) as response:
                data = json.load(response)
                if response.headers.get('Access-Control-Allow-Origin') != args.origin:
                    raise ValueError('CORS does not allow the supplied --origin. Check APP_CORS_ORIGINS on the backend.')
                if path.endswith('/summary'):
                    print(f'PASS: {path}: {data}')
                elif 'items' in data:
                    print(f'PASS: {path}: {len(data["items"])} rows')
                else:
                    print(f'PASS: {path}')
    except (HTTPError, URLError, ValueError) as exc:
        print(f'FAIL: {exc}')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

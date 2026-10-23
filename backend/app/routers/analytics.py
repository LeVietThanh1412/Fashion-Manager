from ipaddress import ip_address, ip_network
from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException, Request
from mysql.connector import ProgrammingError
from pydantic import BaseModel, Field

from app.repositories.analytics import get_visit_dashboard, record_visit

router = APIRouter(prefix='/api/analytics', tags=['analytics'])


class VisitInput(BaseModel):
    path: str = Field(min_length=1, max_length=500, pattern=r'^/[^\r\n]*$')
    referrer: str = Field(default='', max_length=2000)


def device_type(user_agent: str) -> str:
    agent = user_agent.lower()
    if 'ipad' in agent or 'tablet' in agent or ('android' in agent and 'mobile' not in agent):
        return 'tablet'
    return 'mobile' if any(value in agent for value in ('mobile', 'iphone', 'ipod')) else 'desktop'


def masked_ip(host: str) -> str:
    try:
        address = ip_address(host)
        return str(ip_network(f'{address}/{24 if address.version == 4 else 48}', strict=False))
    except ValueError:
        return 'Không xác định'


def clean_referrer(value: str) -> str:
    try:
        parsed = urlsplit(value)
        if parsed.scheme in {'http', 'https'} and parsed.hostname:
            return parsed.hostname[:500]
    except ValueError:
        pass
    return ''


def analytics_not_ready(exc: ProgrammingError) -> None:
    if exc.errno == 1146:
        raise HTTPException(status_code=503, detail='Theo dõi lượt truy cập chưa được thiết lập trên máy chủ.') from exc
    raise exc


@router.post('/visits', status_code=201)
def track_visit(payload: VisitInput, request: Request) -> dict:
    try:
        record_visit(payload.path, masked_ip(request.client.host if request.client else ''), device_type(request.headers.get('user-agent', '')), clean_referrer(payload.referrer))
    except ProgrammingError as exc:
        analytics_not_ready(exc)
    return {'status': 'recorded'}


@router.get('/visits')
def visit_dashboard() -> dict:
    try:
        return get_visit_dashboard()
    except ProgrammingError as exc:
        analytics_not_ready(exc)

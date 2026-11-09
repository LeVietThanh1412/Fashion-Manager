"""One canonical Vietnamese mobile number per employee login."""
import re


def normalize_phone(value: str) -> str:
    compact = re.sub(r'[\s().-]', '', value.strip())
    match = re.fullmatch(r'(?:\+84|84|0)([35789][0-9]{8})', compact)
    if not match:
        raise ValueError('Số điện thoại nhân viên phải là số di động Việt Nam hợp lệ.')
    return '+84' + match.group(1)

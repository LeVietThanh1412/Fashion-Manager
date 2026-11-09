import base64
import hashlib
import hmac
import json
import time
import secrets

from fastapi import HTTPException, status

from app.core.config import settings

TOKEN_LIFETIME_SECONDS = 12 * 60 * 60


def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError('Password must contain at least 12 characters.')
    salt = secrets.token_bytes(16)
    value = hashlib.scrypt(password.encode('utf-8'), salt=salt, n=16384, r=8, p=1)
    return f'scrypt${salt.hex()}${value.hex()}'


def verify_password(password: str, encoded: str | None) -> bool:
    try:
        algorithm, salt, expected = encoded.split('$')
        if algorithm != 'scrypt' or len(salt) != 32 or len(expected) != 128:
            return False
        value = hashlib.scrypt(password.encode('utf-8'), salt=bytes.fromhex(salt), n=16384, r=8, p=1)
        return hmac.compare_digest(value, bytes.fromhex(expected))
    except (AttributeError, ValueError, TypeError):
        return False


def _secret() -> bytes:
    secret = settings.auth_token_secret.encode("utf-8")
    if len(secret) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Backend chưa được cấu hình AUTH_TOKEN_SECRET đủ mạnh.",
        )
    return secret


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_access_token(employee_id: str, auth_version: int = 0) -> tuple[str, int]:
    expires_at = int(time.time()) + TOKEN_LIFETIME_SECONDS
    payload = _encode(json.dumps(
        {
            "sub": employee_id,
            "ver": auth_version,
            "exp": expires_at,
        },
        separators=(",", ":"),
    ).encode("utf-8"))
    signature = _encode(hmac.new(_secret(), payload.encode("ascii"), hashlib.sha256).digest())
    return f"{payload}.{signature}", TOKEN_LIFETIME_SECONDS


def decode_access_token(token: str) -> dict[str, str]:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Phiên đăng nhập không hợp lệ hoặc đã hết hạn.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload, supplied_signature = token.split(".", 1)
        expected_signature = _encode(
            hmac.new(_secret(), payload.encode("ascii"), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(supplied_signature, expected_signature):
            raise unauthorized
        claims = json.loads(_decode(payload))
        if (
            not isinstance(claims.get("sub"), str)
            or not isinstance(claims.get("ver"), int)
            or int(claims["exp"]) <= int(time.time())
        ):
            raise unauthorized
        return {
            "employee_id": claims["sub"],
            "auth_version": claims["ver"],
        }
    except HTTPException:
        raise
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        raise unauthorized from None

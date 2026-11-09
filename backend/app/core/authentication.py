from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.security import decode_access_token
from app.repositories.auth import get_user_by_id
from app.permissions import require_permission, has_system_permission

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)):
    if credentials is None or credentials.scheme.lower() != 'bearer':
        raise HTTPException(401, 'Please sign in.', headers={'WWW-Authenticate':'Bearer'})
    claims = decode_access_token(credentials.credentials)
    user = get_user_by_id(claims['employee_id'])
    if not user or user['trang_thai'] != 'active' or user['auth_version'] != claims['auth_version']:
        raise HTTPException(401, 'Account inactive.')
    return user


def require_permissions(permission, system=False):
    def dependency(user=Depends(get_current_user)):
        require_permission(user, permission)
        if system and not has_system_permission(user,permission):
            raise HTTPException(403, 'A system-wide assignment is required.')
        return user
    return dependency

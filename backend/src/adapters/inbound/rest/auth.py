"""
Inbound REST auth dependency — validates the Bearer JWT and resolves the
current user. Raises 401 on missing/invalid/expired tokens.

The credential port and user repository are stored on ``app.state`` by the
composition root (see app.py), keeping this module free of global mutable
state.
"""
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.domain.models import User, UserRole

_bearer_scheme = HTTPBearer(auto_error=False)


def _ports(request: Request):
    credential_port = getattr(request.app.state, "credential_port", None)
    user_repo = getattr(request.app.state, "user_repo", None)
    if credential_port is None or user_repo is None:
        raise HTTPException(status_code=500, detail="Auth services not initialized.")
    return credential_port, user_repo


def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> User:
    credential_port, user_repo = _ports(request)
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Provide a Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = credential_port.decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = user_repo.get_by_id(payload.get("sub", ""))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found or inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_role(*allowed: UserRole):
    """Dependency factory restricting a route to specific roles."""

    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {[r.value for r in allowed]}.",
            )
        return current_user

    return _check

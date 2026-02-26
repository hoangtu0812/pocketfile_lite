"""
FastAPI dependency injection providers.
Provides database sessions, current user, and role guards.
"""

from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User, UserRole

bearer_scheme = HTTPBearer(auto_error=False)


# ─── Database ─────────────────────────────────────────────────────────────────


def get_db():
    """Yield a SQLAlchemy database session and close it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbDep = Annotated[Session, Depends(get_db)]


# ─── Authentication ───────────────────────────────────────────────────────────


def get_current_user(
    db: DbDep,
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
    token: Optional[str] = Query(None),
) -> User:
    """
    Extract and validate the JWT from the Authorization header or query parameter.

    Raises:
        HTTPException 401 if token is invalid or user not found.
    """
    actual_token = None
    if credentials:
        actual_token = credentials.credentials
    elif token:
        actual_token = token

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not actual_token:
        raise credentials_exception

    payload = decode_access_token(actual_token)
    if payload is None:
        raise credentials_exception

    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


# ─── Role Guards ──────────────────────────────────────────────────────────────


def require_admin(current_user: CurrentUser) -> User:
    """
    Ensure the current user has ADMIN role.

    Raises:
        HTTPException 403 if user is not an admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


AdminUser = Annotated[User, Depends(require_admin)]

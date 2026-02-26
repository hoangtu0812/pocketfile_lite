"""
Auth API routes: login and register.
"""

from fastapi import APIRouter

from app.core.dependencies import AdminUser, DbDep
from app.schemas.common import BaseResponse
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserRead
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=BaseResponse[TokenResponse])
def login(payload: LoginRequest, db: DbDep):
    """Authenticate user and return JWT access token."""
    service = AuthService(db)
    token_data = service.login(payload)
    return BaseResponse.ok(token_data)


@router.post("/register", response_model=BaseResponse[UserRead])
def register(payload: UserCreate, db: DbDep, _admin: AdminUser):
    """Register a new user account. Admin only."""
    service = AuthService(db)
    user = service.register(payload)
    return BaseResponse.ok(user)

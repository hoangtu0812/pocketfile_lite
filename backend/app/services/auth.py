"""
Authentication service: login, register, token generation.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserRead
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def login(self, credentials: LoginRequest) -> TokenResponse:
        """
        Authenticate user and return JWT token.

        Raises:
            HTTPException 401 if credentials are invalid.
        """
        user = self.repo.get_by_username(credentials.username)
        if not user or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        token = create_access_token({"sub": str(user.id), "role": user.role.value})
        logger.info(f"User '{user.username}' logged in.")
        return TokenResponse(access_token=token, user=UserRead.model_validate(user))

    def register(self, payload: UserCreate) -> UserRead:
        """
        Create a new user account.

        Raises:
            HTTPException 409 if username/email already taken.
        """
        if self.repo.get_by_username(payload.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username '{payload.username}' is already taken",
            )
        if self.repo.get_by_email(payload.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{payload.email}' is already registered",
            )

        user = User(
            username=payload.username,
            email=payload.email,
            password_hash=hash_password(payload.password),
            role=payload.role,
        )
        user = self.repo.create(user)
        logger.info(f"Registered new user '{user.username}' with role {user.role}.")
        return UserRead.model_validate(user)

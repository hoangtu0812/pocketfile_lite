"""
Users API routes: list, delete users (Admin only).
"""

from typing import List

from fastapi import APIRouter

from app.core.dependencies import AdminUser, DbDep
from app.schemas.common import BaseResponse
from app.schemas.user import UserRead, UserUpdatePassword, UserProjectAssign
from app.services.user import UserService

router = APIRouter(tags=["Users"])


@router.get("/users", response_model=BaseResponse[List[UserRead]])
def list_users(db: DbDep, _admin: AdminUser):
    """List all users. Admin only."""
    service = UserService(db)
    users = service.list_users()
    return BaseResponse.ok(users)


@router.delete("/users/{user_id}", response_model=BaseResponse[None])
def delete_user(user_id: int, db: DbDep, current_admin: AdminUser):
    """Delete a user. Admin only."""
    service = UserService(db)
    service.delete_user(current_user=current_admin, target_user_id=user_id)
    return BaseResponse.ok(None)


@router.patch("/users/{user_id}/password", response_model=BaseResponse[UserRead])
def update_user_password(
    user_id: int, payload: UserUpdatePassword, db: DbDep, _admin: AdminUser
):
    """Update a user's password. Admin only."""
    service = UserService(db)
    user = service.update_password(user_id, payload.password)
    return BaseResponse.ok(user)


@router.get("/users/{user_id}/projects", response_model=BaseResponse[list[int]])
def get_user_projects(user_id: int, db: DbDep, _admin: AdminUser):
    """Get project IDs assigned to a user. Admin only."""
    service = UserService(db)
    projects = service.get_user_projects(user_id)
    return BaseResponse.ok(projects)


@router.put("/users/{user_id}/projects", response_model=BaseResponse[None])
def assign_user_projects(
    user_id: int, payload: UserProjectAssign, db: DbDep, _admin: AdminUser
):
    """Assign projects to a user. Admin only."""
    service = UserService(db)
    service.assign_user_projects(user_id, payload.project_ids)
    return BaseResponse.ok(None)

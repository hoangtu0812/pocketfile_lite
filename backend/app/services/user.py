"""
User service — business logic for user management.
"""

from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.schemas.user import UserRead


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def list_users(self) -> List[UserRead]:
        """List all users."""
        users = self.repo.get_all(skip=0, limit=1000)
        return [
            UserRead(
                id=u.id,
                username=u.username,
                email=u.email,
                role=u.role,
                created_at=u.created_at,
            )
            for u in users
        ]

    def delete_user(self, current_user: User, target_user_id: int):
        """Delete a user. Prevent deleting self or the only admin."""
        if current_user.id == target_user_id:
            raise HTTPException(status_code=400, detail="Cannot delete your own account")

        target_user = self.repo.get(target_user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Optionally prevent deleting if they are the only Admin left
        if target_user.role == UserRole.ADMIN:
            admin_count = len([u for u in self.repo.get_all(0, 1000) if u.role == UserRole.ADMIN])
            if admin_count <= 1:
                raise HTTPException(status_code=400, detail="Cannot delete the last admin account")

        self.repo.delete(target_user)

    def update_password(self, target_user_id: int, new_password: str):
        """Update a user's password."""
        target_user = self.repo.get(target_user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        from app.core.security import hash_password
        target_user.hashed_password = hash_password(new_password)
        self.repo.update(target_user)
        return target_user

    def get_user_projects(self, user_id: int) -> list[int]:
        """Get list of project IDs assigned to a user."""
        user = self.repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return [p.id for p in user.projects]

    def assign_user_projects(self, user_id: int, project_ids: list[int]):
        """Assign list of project IDs to a user."""
        user = self.repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        from app.models.project import Project
        projects = self.repo.db.query(Project).filter(Project.id.in_(project_ids)).all()
        user.projects = projects
        self.repo.update(user)

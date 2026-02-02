"""User career path repository."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from upskills.models.db.progress import UserCareerPath, UserPathAssignment
from upskills.repositories.base import BaseRepository


class UserCareerPathRepository(BaseRepository[UserCareerPath]):
    """Repository for UserCareerPath operations."""

    async def get_by_id(
        self, user_career_path_id: int, id_column: str = "user_career_path_id"
    ) -> UserCareerPath | None:
        """Get user career path by ID with related data."""
        async with self._db_provider.session() as session:
            stmt = (
                select(UserCareerPath)
                .options(
                    selectinload(UserCareerPath.career),
                    selectinload(UserCareerPath.path_assignments).selectinload(
                        UserPathAssignment.path_template
                    ),
                )
                .where(UserCareerPath.user_career_path_id == user_career_path_id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> list[UserCareerPath]:
        """Get all career paths for a user."""
        async with self._db_provider.session() as session:
            stmt = (
                select(UserCareerPath)
                .options(
                    selectinload(UserCareerPath.career),
                    selectinload(UserCareerPath.path_assignments),
                )
                .where(UserCareerPath.user_id == user_id)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_active_for_user(self, user_id: int) -> UserCareerPath | None:
        """Get the current active career path for a user (most recent)."""
        async with self._db_provider.session() as session:
            stmt = (
                select(UserCareerPath)
                .options(
                    selectinload(UserCareerPath.career),
                    selectinload(UserCareerPath.path_assignments).selectinload(
                        UserPathAssignment.path_template
                    ),
                )
                .where(UserCareerPath.user_id == user_id)
                .order_by(UserCareerPath.start_date.desc())
                .limit(1)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

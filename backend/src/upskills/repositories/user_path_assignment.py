"""User path assignment repository."""

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from upskills.models.db.career import PathTemplate
from upskills.models.db.progress import UserCareerPath, UserPathAssignment
from upskills.repositories.base import BaseRepository


class UserPathAssignmentRepository(BaseRepository[UserPathAssignment]):
    """Repository for UserPathAssignment operations."""

    async def get_by_id(
        self, assignment_id: int, id_column: str = "user_path_assignment_id"
    ) -> UserPathAssignment | None:
        """Get path assignment by ID with related data."""
        async with self._db_provider.session() as session:
            stmt = (
                select(UserPathAssignment)
                .options(
                    selectinload(UserPathAssignment.path_template).selectinload(PathTemplate.steps),
                    selectinload(UserPathAssignment.step_progress),
                )
                .where(UserPathAssignment.user_path_assignment_id == assignment_id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_career_path(self, user_career_path_id: int) -> list[UserPathAssignment]:
        """Get all path assignments for a career path."""
        async with self._db_provider.session() as session:
            stmt = (
                select(UserPathAssignment)
                .options(
                    selectinload(UserPathAssignment.path_template),
                    selectinload(UserPathAssignment.step_progress),
                )
                .where(UserPathAssignment.user_career_path_id == user_career_path_id)
                .order_by(UserPathAssignment.start_date)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_pending_validation(
        self, mentor_user_id: int | None = None
    ) -> list[UserPathAssignment]:
        """Get all assignments pending mentor validation."""
        async with self._db_provider.session() as session:
            stmt = (
                select(UserPathAssignment)
                .options(
                    selectinload(UserPathAssignment.path_template),
                    selectinload(UserPathAssignment.user_career_path).selectinload(UserCareerPath.user),
                )
                .where(
                    UserPathAssignment.status == "Completed",
                    UserPathAssignment.mentor_validation_status == "Pending",
                )
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def count_completed_for_career_path(self, user_career_path_id: int) -> tuple[int, int]:
        """Count completed and total assignments for a career path."""
        async with self._db_provider.session() as session:
            total_stmt = (
                select(func.count())
                .select_from(UserPathAssignment)
                .where(UserPathAssignment.user_career_path_id == user_career_path_id)
            )
            completed_stmt = (
                select(func.count())
                .select_from(UserPathAssignment)
                .where(
                    UserPathAssignment.user_career_path_id == user_career_path_id,
                    UserPathAssignment.mentor_validation_status == "Approved",
                )
            )

            total_result = await session.execute(total_stmt)
            completed_result = await session.execute(completed_stmt)

            return completed_result.scalar() or 0, total_result.scalar() or 0

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from upskills.domain import UserCareerPath as UserCareerPathDomain
from upskills.repositories.base import BaseRepository
from upskills.repositories.user_path_assignment.models import UserPathAssignment

from .models import UserCareerPath


class UserCareerPathRepository(BaseRepository[UserCareerPath]):
    async def get_by_id(self, id_value: int, id_column: str = "user_career_path_id") -> UserCareerPath | None:
        async with self._db_provider.session() as session:
            stmt = (
                select(UserCareerPath)
                .options(
                    selectinload(UserCareerPath.career),
                    selectinload(UserCareerPath.path_assignments).selectinload(UserPathAssignment.path_template),
                )
                .where(UserCareerPath.user_career_path_id == id_value)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> list[UserCareerPathDomain]:
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
            return [self.to_domain(p, include_assignments=True) for p in result.scalars().all()]

    async def get_active_for_user(self, user_id: int) -> UserCareerPath | None:
        async with self._db_provider.session() as session:
            stmt = (
                select(UserCareerPath)
                .options(
                    selectinload(UserCareerPath.career),
                    selectinload(UserCareerPath.path_assignments).selectinload(UserPathAssignment.path_template),
                    selectinload(UserCareerPath.path_assignments).selectinload(UserPathAssignment.path_template),
                )
                .where(UserCareerPath.user_id == user_id)
                .order_by(UserCareerPath.start_date.desc())
                .limit(1)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    @staticmethod
    def to_domain(path: UserCareerPath, *, include_assignments: bool = False) -> UserCareerPathDomain:
        path_dict = path.to_dict()
        if not include_assignments and "path_assignments" in path_dict:
            path_dict.pop("path_assignments")
        return UserCareerPathDomain.model_validate(path_dict)

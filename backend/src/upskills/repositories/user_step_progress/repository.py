from sqlalchemy import select
from sqlalchemy.orm import selectinload

from upskills.domain import UserStepProgress as UserStepProgressDomain
from upskills.repositories.base import BaseRepository

from .models import UserStepProgress


class UserStepProgressRepository(BaseRepository[UserStepProgress]):
    async def get_by_id(self, id_value: int, id_column: str = "user_step_progress_id") -> UserStepProgress | None:
        async with self._db_provider.session() as session:
            stmt = (
                select(UserStepProgress)
                .options(selectinload(UserStepProgress.step))
                .where(UserStepProgress.user_step_progress_id == id_value)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_assignment(self, user_path_assignment_id: int) -> list[UserStepProgressDomain]:
        async with self._db_provider.session() as session:
            stmt = (
                select(UserStepProgress)
                .options(selectinload(UserStepProgress.step))
                .where(UserStepProgress.user_path_assignment_id == user_path_assignment_id)
                .order_by(UserStepProgress.step_id)
            )
            result = await session.execute(stmt)
            return [self.to_domain(p) for p in result.scalars().all()]

    async def get_or_create(self, user_path_assignment_id: int, step_id: int) -> UserStepProgress:
        async with self._db_provider.session() as session:
            stmt = select(UserStepProgress).where(
                UserStepProgress.user_path_assignment_id == user_path_assignment_id,
                UserStepProgress.step_id == step_id,
            )
            result = await session.execute(stmt)
            progress = result.scalar_one_or_none()

            if not progress:
                progress = UserStepProgress(
                    user_path_assignment_id=user_path_assignment_id,
                    step_id=step_id,
                )
                session.add(progress)
                await session.flush()
                await session.commit()
                await session.refresh(progress)

            return progress

    @staticmethod
    def to_domain(progress: UserStepProgress) -> UserStepProgressDomain:
        return UserStepProgressDomain.model_validate(progress.to_dict())

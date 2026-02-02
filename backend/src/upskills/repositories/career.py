"""Career repository."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from upskills.models.db.career import Career
from upskills.repositories.base import BaseRepository


class CareerRepository(BaseRepository[Career]):
    """Repository for Career operations."""

    async def get_by_id(self, career_id: int, id_column: str = "career_id") -> Career | None:
        """Get career by ID with path templates."""
        async with self._db_provider.session() as session:
            stmt = (
                select(Career)
                .options(selectinload(Career.path_templates))
                .where(Career.career_id == career_id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_all_with_paths(self, *, skip: int = 0, limit: int = 100) -> list[Career]:
        """Get all careers with their path templates."""
        async with self._db_provider.session() as session:
            stmt = select(Career).options(selectinload(Career.path_templates)).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())

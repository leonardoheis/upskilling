"""Path template repository."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from upskills.models.db.career import PathTemplate, PathTemplateStep
from upskills.repositories.base import BaseRepository


class PathTemplateRepository(BaseRepository[PathTemplate]):
    """Repository for PathTemplate operations."""

    async def get_by_id(
        self, path_template_id: int, id_column: str = "path_template_id"
    ) -> PathTemplate | None:
        """Get path template by ID with steps."""
        async with self._db_provider.session() as session:
            stmt = (
                select(PathTemplate)
                .options(
                    selectinload(PathTemplate.career),
                    selectinload(PathTemplate.steps).selectinload(PathTemplateStep.dependencies),
                )
                .where(PathTemplate.path_template_id == path_template_id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_career(self, career_id: int) -> list[PathTemplate]:
        """Get all path templates for a career."""
        async with self._db_provider.session() as session:
            stmt = (
                select(PathTemplate)
                .options(selectinload(PathTemplate.steps))
                .where(PathTemplate.career_id == career_id)
                .order_by(PathTemplate.default_start_offset_days)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_all_with_details(self, *, skip: int = 0, limit: int = 100) -> list[PathTemplate]:
        """Get all path templates with career and steps."""
        async with self._db_provider.session() as session:
            stmt = (
                select(PathTemplate)
                .options(
                    selectinload(PathTemplate.career),
                    selectinload(PathTemplate.steps),
                )
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

"""Path step repository."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from upskills.models.db.career import PathStepDependency, PathTemplateStep
from upskills.repositories.base import BaseRepository


class PathStepRepository(BaseRepository[PathTemplateStep]):
    """Repository for PathTemplateStep operations."""

    async def get_by_id(self, step_id: int, id_column: str = "step_id") -> PathTemplateStep | None:
        """Get step by ID with dependencies."""
        async with self._db_provider.session() as session:
            stmt = (
                select(PathTemplateStep)
                .options(selectinload(PathTemplateStep.dependencies))
                .where(PathTemplateStep.step_id == step_id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_path_template(self, path_template_id: int) -> list[PathTemplateStep]:
        """Get all steps for a path template, ordered by step_order."""
        async with self._db_provider.session() as session:
            stmt = (
                select(PathTemplateStep)
                .options(selectinload(PathTemplateStep.dependencies))
                .where(PathTemplateStep.path_template_id == path_template_id)
                .order_by(PathTemplateStep.step_order)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def add_dependency(self, step_id: int, depends_on_step_id: int) -> None:
        """Add a dependency between steps."""
        async with self._db_provider.session() as session:
            dep = PathStepDependency(step_id=step_id, depends_on_step_id=depends_on_step_id)
            session.add(dep)
            await session.flush()
            await session.commit()

    async def remove_dependency(self, step_id: int, depends_on_step_id: int) -> None:
        """Remove a dependency between steps."""
        async with self._db_provider.session() as session:
            stmt = select(PathStepDependency).where(
                PathStepDependency.step_id == step_id,
                PathStepDependency.depends_on_step_id == depends_on_step_id,
            )
            result = await session.execute(stmt)
            dep = result.scalar_one_or_none()
            if dep:
                await session.delete(dep)
                await session.flush()
                await session.commit()

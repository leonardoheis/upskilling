"""Path step service."""

from dependency_injector.wiring import Provide, inject

from upskills.models.db.career import PathTemplateStep
from upskills.models.domain.career import (
    PathStepCreateInput,
    PathStepDependencyResponse,
    PathStepResponse,
    PathStepUpdateInput,
)
from upskills.repositories.path_step import PathStepRepository
from upskills.repositories.path_template import PathTemplateRepository


class PathStepService:
    """Service for path step operations."""

    @inject
    def __init__(
        self,
        path_step_repository: PathStepRepository = Provide["path_step_repository"],
        path_template_repository: PathTemplateRepository = Provide["path_template_repository"],
    ) -> None:
        self._path_step_repository = path_step_repository
        self._path_template_repository = path_template_repository

    async def get_step(self, step_id: int) -> PathStepResponse | None:
        """Get a step by ID."""
        step = await self._path_step_repository.get_by_id(step_id)
        if not step:
            return None
        return self._step_to_response(step)

    async def get_steps_for_path(self, path_template_id: int) -> list[PathStepResponse]:
        """Get all steps for a path template."""
        steps = await self._path_step_repository.get_by_path_template(path_template_id)
        return [self._step_to_response(s) for s in steps]

    async def create_step(
        self,
        data: PathStepCreateInput,
    ) -> PathStepResponse:
        """Create a new step."""
        # Verify path exists
        path = await self._path_template_repository.get_by_id(data.path_template_id)
        if not path:
            msg = "Path template not found"
            raise ValueError(msg)

        step = await self._path_step_repository.create(data.model_dump())
        return self._step_to_response(step)

    async def update_step(
        self,
        step_id: int,
        data: PathStepUpdateInput,
    ) -> PathStepResponse | None:
        """Update a step."""
        step = await self._path_step_repository.get_by_id(step_id)
        if not step:
            return None

        update_data = data.model_dump(exclude_unset=True)

        if update_data:
            step = await self._path_step_repository.update(step, update_data)

        return self._step_to_response(step)

    async def delete_step(self, step_id: int) -> bool:
        """Delete a step."""
        step = await self._path_step_repository.get_by_id(step_id)
        if not step:
            return False

        await self._path_step_repository.delete(step)
        return True

    async def add_dependency(self, step_id: int, depends_on_step_id: int) -> bool:
        """Add a dependency between steps."""
        await self._path_step_repository.add_dependency(step_id, depends_on_step_id)
        return True

    async def remove_dependency(self, step_id: int, depends_on_step_id: int) -> bool:
        """Remove a dependency between steps."""
        await self._path_step_repository.remove_dependency(step_id, depends_on_step_id)
        return True

    @staticmethod
    def _step_to_response(step: PathTemplateStep) -> PathStepResponse:
        """Convert PathTemplateStep to PathStepResponse."""
        deps: list[PathStepDependencyResponse] = []
        if step.dependencies:
            deps.extend(
                PathStepDependencyResponse(
                    depends_on_step_id=dep.depends_on_step_id,
                    depends_on_step_name=dep.depends_on_step.name if dep.depends_on_step else "",
                )
                for dep in step.dependencies
            )

        return PathStepResponse(
            step_id=step.step_id,
            path_template_id=step.path_template_id,
            step_order=step.step_order,
            name=step.name,
            description=step.description,
            duration_hours=step.duration_hours,
            course_link=step.course_link,
            dependencies=deps,
        )

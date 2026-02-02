"""Path template service."""

from typing import Any

from dependency_injector.wiring import Provide, inject

from upskills.models.db.career import PathTemplate
from upskills.models.domain.career import (
    PathStepResponse,
    PathTemplateCreateInput,
    PathTemplateResponse,
    PathTemplateUpdateInput,
    PathTemplateWithStepsResponse,
    PathStepDependencyResponse,
)
from upskills.repositories.career import CareerRepository
from upskills.repositories.path_step import PathStepRepository
from upskills.repositories.path_template import PathTemplateRepository


class PathTemplateService:
    """Service for path template operations."""

    @inject
    def __init__(
        self,
        path_template_repository: PathTemplateRepository = Provide["path_template_repository"],
        path_step_repository: PathStepRepository = Provide["path_step_repository"],
        career_repository: CareerRepository = Provide["career_repository"],
    ) -> None:
        self._path_template_repository = path_template_repository
        self._path_step_repository = path_step_repository
        self._career_repository = career_repository

    async def get_path(self, path_template_id: int) -> PathTemplateWithStepsResponse | None:
        """Get a path template by ID with steps."""
        path = await self._path_template_repository.get_by_id(path_template_id)
        if not path:
            return None
        return self._path_to_response_with_steps(path)

    async def get_all_paths(
        self, *, skip: int = 0, limit: int = 100, career_id: int | None = None
    ) -> tuple[list[PathTemplateResponse], int]:
        """Get all path templates."""
        if career_id:
            paths = await self._path_template_repository.get_by_career(career_id)
            return [self._path_to_response(p) for p in paths], len(paths)

        paths = await self._path_template_repository.get_all_with_details(skip=skip, limit=limit)
        total = await self._path_template_repository.count()

        return [self._path_to_response(p) for p in paths], total

    async def create_path(
        self,
        data: PathTemplateCreateInput,
    ) -> PathTemplateResponse:
        """Create a new path template."""
        # Verify career exists
        career = await self._career_repository.get_by_id(data.career_id)
        if not career:
            msg = "Career not found"
            raise ValueError(msg)

        path = await self._path_template_repository.create(data.model_dump())
        return self._path_to_response(path)

    async def update_path(
        self,
        path_template_id: int,
        data: PathTemplateUpdateInput,
    ) -> PathTemplateResponse | None:
        """Update a path template."""
        path = await self._path_template_repository.get_by_id(path_template_id)
        if not path:
            return None

        update_data = data.model_dump(exclude_unset=True)

        if update_data:
            path = await self._path_template_repository.update(path, update_data)

        return self._path_to_response(path)

    async def delete_path(self, path_template_id: int) -> bool:
        """Delete a path template."""
        path = await self._path_template_repository.get_by_id(path_template_id)
        if not path:
            return False

        await self._path_template_repository.delete(path)
        return True

    @staticmethod
    def _path_to_response(path: PathTemplate) -> PathTemplateResponse:
        """Convert PathTemplate to PathTemplateResponse."""
        return PathTemplateResponse(
            path_template_id=path.path_template_id,
            career_id=path.career_id,
            name=path.name,
            description=path.description,
            duration_hours=path.duration_hours,
            default_start_offset_days=path.default_start_offset_days,
            default_deadline_offset_days=path.default_deadline_offset_days,
        )

    @staticmethod
    def _path_to_response_with_steps(path: PathTemplate) -> PathTemplateWithStepsResponse:
        """Convert PathTemplate to PathTemplateWithStepsResponse."""
        steps: list[PathStepResponse] = []
        if path.steps:
            for step in path.steps:
                deps: list[PathStepDependencyResponse] = []
                if step.dependencies:
                    deps.extend(
                        PathStepDependencyResponse(
                            depends_on_step_id=dep.depends_on_step_id,
                            depends_on_step_name=dep.depends_on_step.name
                            if dep.depends_on_step
                            else "",
                        )
                        for dep in step.dependencies
                    )

                steps.append(
                    PathStepResponse(
                        step_id=step.step_id,
                        path_template_id=step.path_template_id,
                        step_order=step.step_order,
                        name=step.name,
                        description=step.description,
                        duration_hours=step.duration_hours,
                        course_link=step.course_link,
                        dependencies=deps,
                    )
                )

        return PathTemplateWithStepsResponse(
            path_template_id=path.path_template_id,
            career_id=path.career_id,
            name=path.name,
            description=path.description,
            duration_hours=path.duration_hours,
            default_start_offset_days=path.default_start_offset_days,
            default_deadline_offset_days=path.default_deadline_offset_days,
            steps=steps,
        )

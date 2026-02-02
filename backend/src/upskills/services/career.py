"""Career service."""

from typing import Any

from dependency_injector.wiring import Provide, inject

from upskills.models.db.career import Career
from upskills.models.domain.career import (
    CareerResponse,
    CareerWithPathsResponse,
    PathTemplateResponse,
)
from upskills.repositories.career import CareerRepository
from upskills.repositories.path_template import PathTemplateRepository


class CareerService:
    """Service for career operations."""

    @inject
    def __init__(
        self,
        career_repository: CareerRepository = Provide["career_repository"],
        path_template_repository: PathTemplateRepository = Provide["path_template_repository"],
    ) -> None:
        self._career_repository = career_repository
        self._path_template_repository = path_template_repository

    async def get_career(self, career_id: int) -> CareerWithPathsResponse | None:
        """Get a career by ID with its paths."""
        career = await self._career_repository.get_by_id(career_id)
        if not career:
            return None
        return self._career_to_response_with_paths(career)

    async def get_all_careers(
        self, *, skip: int = 0, limit: int = 100
    ) -> tuple[list[CareerResponse], int]:
        """Get all careers."""
        careers = await self._career_repository.get_all_with_paths(skip=skip, limit=limit)
        total = await self._career_repository.count()

        return [self._career_to_response(c) for c in careers], total

    async def create_career(
        self,
        name: str,
        specialization: str | None = None,
    ) -> CareerResponse:
        """Create a new career."""
        career = await self._career_repository.create({
            "name": name,
            "specialization": specialization,
        })
        return self._career_to_response(career)

    async def update_career(
        self,
        career_id: int,
        name: str | None = None,
        specialization: str | None = None,
    ) -> CareerResponse | None:
        """Update a career."""
        career = await self._career_repository.get_by_id(career_id)
        if not career:
            return None

        update_data: dict[str, Any] = {}
        if name is not None:
            update_data["name"] = name
        if specialization is not None:
            update_data["specialization"] = specialization

        if update_data:
            career = await self._career_repository.update(career, update_data)

        return self._career_to_response(career)

    async def delete_career(self, career_id: int) -> bool:
        """Delete a career."""
        career = await self._career_repository.get_by_id(career_id)
        if not career:
            return False

        await self._career_repository.delete(career)
        return True

    @staticmethod
    def _career_to_response(career: Career) -> CareerResponse:
        """Convert Career to CareerResponse."""
        return CareerResponse(
            career_id=career.career_id,
            name=career.name,
            specialization=career.specialization,
        )

    @staticmethod
    def _career_to_response_with_paths(career: Career) -> CareerWithPathsResponse:
        """Convert Career to CareerWithPathsResponse."""
        paths = []
        if career.path_templates:
            paths = [
                PathTemplateResponse(
                    path_template_id=p.path_template_id,
                    career_id=p.career_id,
                    name=p.name,
                    description=p.description,
                    duration_hours=p.duration_hours,
                    default_start_offset_days=p.default_start_offset_days,
                    default_deadline_offset_days=p.default_deadline_offset_days,
                )
                for p in career.path_templates
            ]

        return CareerWithPathsResponse(
            career_id=career.career_id,
            name=career.name,
            specialization=career.specialization,
            path_templates=paths,
        )

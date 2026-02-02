"""Path steps router."""

from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from upskills.core.dependencies import CurrentUser, require_permissions
from upskills.models.db.user import User
from upskills.models.domain.base import MessageResponse
from upskills.models.domain.career import (
    PathStepCreate,
    PathStepCreateInput,
    PathStepResponse,
    PathStepUpdate,
    PathStepUpdateInput,
    StepDependencyCreate,
)
from upskills.services.path_step import PathStepService

router = APIRouter()


@router.get("/templates/{path_id}/steps")
@inject
async def list_steps(
    path_id: int,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
    current_user: CurrentUser,
) -> list[PathStepResponse]:
    """Get all steps for a path template."""
    return await service.get_steps_for_path(path_id)


@router.post("/templates/{path_id}/steps", status_code=status.HTTP_201_CREATED)
@inject
async def create_step(
    path_id: int,
    data: PathStepCreate,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
    _: Annotated[User, Depends(require_permissions("path_content.add"))],
) -> PathStepResponse:
    """Create a new step (requires path_content.add permission)."""
    try:
        input_data = PathStepCreateInput(
            path_template_id=path_id,
            step_order=data.step_order,
            name=data.name,
            description=data.description,
            duration_hours=data.duration_hours,
            course_link=data.course_link,
        )
        result = await service.create_step(input_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/{step_id}")
@inject
async def get_step(
    step_id: int,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
    current_user: CurrentUser,
) -> PathStepResponse:
    """Get a specific step."""
    result = await service.get_step(step_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found",
        )

    return result


@router.put("/{step_id}")
@inject
async def update_step(
    step_id: int,
    data: PathStepUpdate,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
    _: Annotated[User, Depends(require_permissions("path_content.add"))],
) -> PathStepResponse:
    """Update a step (requires path_content.add permission)."""
    input_data = PathStepUpdateInput(
        step_order=data.step_order,
        name=data.name,
        description=data.description,
        duration_hours=data.duration_hours,
        course_link=data.course_link,
    )
    result = await service.update_step(step_id, input_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found",
        )

    return result


@router.delete("/{step_id}")
@inject
async def delete_step(
    step_id: int,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
    _: Annotated[User, Depends(require_permissions("path_content.add"))],
) -> MessageResponse:
    """Delete a step (requires path_content.add permission)."""
    success = await service.delete_step(step_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found",
        )

    return MessageResponse(message="Step deleted successfully.")


@router.post("/{step_id}/dependencies")
@inject
async def add_step_dependency(
    step_id: int,
    data: StepDependencyCreate,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
    _: Annotated[User, Depends(require_permissions("path_content.add"))],
) -> MessageResponse:
    """Add a dependency to a step (requires path_content.add permission)."""
    await service.add_dependency(step_id, data.depends_on_step_id)
    return MessageResponse(message="Dependency added successfully.")


@router.delete("/{step_id}/dependencies/{depends_on_step_id}")
@inject
async def remove_step_dependency(
    step_id: int,
    depends_on_step_id: int,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
    _: Annotated[User, Depends(require_permissions("path_content.add"))],
) -> MessageResponse:
    """Remove a dependency from a step (requires path_content.add permission)."""
    await service.remove_dependency(step_id, depends_on_step_id)
    return MessageResponse(message="Dependency removed successfully.")

from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from upskills.api.dependencies import get_optional_user, require_permissions
from upskills.api.schemas import MessageResponse
from upskills.domain import PathStep
from upskills.services import PathStepService

from .schemas import (
    PathStepCreate,
    PathStepResponse,
    PathStepUpdate,
    StepDependencyCreate,
)

router = APIRouter(prefix="/steps", tags=["Path Steps"])


@router.get("/templates/{path_id}/steps", dependencies=[Depends(get_optional_user)])
@inject
async def list_steps(
    path_id: int,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
) -> list[PathStepResponse]:
    results = await service.get_steps_for_path(path_id)
    return [PathStepResponse.model_validate(r.model_dump()) for r in results]


@router.post(
    "/templates/{path_id}/steps",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions("path_content.add"))],
)
@inject
async def create_step(
    path_id: int,
    data: PathStepCreate,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
) -> PathStepResponse:
    step = PathStep(
        step_order=data.step_order,
        name=data.name,
        description=data.description,
        duration_hours=data.duration_hours,
        course_link=data.course_link,
    )
    result = await service.create_step(path_id, step)
    return PathStepResponse.model_validate(result.model_dump())


@router.get("/{step_id}", dependencies=[Depends(get_optional_user)])
@inject
async def get_step(
    step_id: int,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
) -> PathStepResponse:
    result = await service.get_step(step_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found",
        )

    return PathStepResponse.model_validate(result.model_dump())


@router.put("/{step_id}", dependencies=[Depends(require_permissions("path_content.add"))])
@inject
async def update_step(
    step_id: int,
    data: PathStepUpdate,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
) -> PathStepResponse:
    step = PathStep(
        step_order=data.step_order,
        name=data.name,
        description=data.description,
        duration_hours=data.duration_hours,
        course_link=data.course_link,
    )
    result = await service.update_step(step_id, step)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found",
        )

    return PathStepResponse.model_validate(result.model_dump())


@router.delete("/{step_id}", dependencies=[Depends(require_permissions("path_content.add"))])
@inject
async def delete_step(
    step_id: int,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
) -> MessageResponse:
    success = await service.delete_step(step_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found",
        )

    return MessageResponse(message="Step deleted successfully.")


@router.post("/{step_id}/dependencies", dependencies=[Depends(require_permissions("path_content.add"))])
@inject
async def add_step_dependency(
    step_id: int,
    data: StepDependencyCreate,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
) -> MessageResponse:
    await service.add_dependency(step_id, data.depends_on_step_id)
    return MessageResponse(message="Dependency added successfully.")


@router.delete(
    "/{step_id}/dependencies/{depends_on_step_id}", dependencies=[Depends(require_permissions("path_content.add"))]
)
@inject
async def remove_step_dependency(
    step_id: int,
    depends_on_step_id: int,
    service: Annotated[PathStepService, Depends(Provide["path_step_service"])],
) -> MessageResponse:
    await service.remove_dependency(step_id, depends_on_step_id)
    return MessageResponse(message="Dependency removed successfully.")

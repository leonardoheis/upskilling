from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from upskills.api.dependencies import get_optional_user, require_permissions
from upskills.api.schemas import MessageResponse, PaginatedResponse
from upskills.domain import PathTemplate
from upskills.services import PathTemplateService

from .schemas import PathTemplateCreate, PathTemplateResponse, PathTemplateUpdate, PathTemplateWithStepsResponse

router = APIRouter(prefix="/paths", tags=["Path Templates"])


@router.get("", dependencies=[Depends(get_optional_user)])
@inject
async def list_paths(
    service: Annotated[PathTemplateService, Depends(Provide["path_template_service"])],
    career_id: int | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[PathTemplateResponse]:
    skip = (page - 1) * page_size

    paths, total = await service.get_all(skip=skip, limit=page_size, career_id=career_id)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    items = [PathTemplateResponse.model_validate(p.model_dump()) for p in paths]

    return PaginatedResponse[PathTemplateResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post(
    "", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions("path_template.create"))]
)
@inject
async def create_path(
    data: PathTemplateCreate,
    service: Annotated[PathTemplateService, Depends(Provide["path_template_service"])],
) -> PathTemplateResponse:
    path = PathTemplate(
        career_id=data.career_id,
        name=data.name,
        description=data.description,
        duration_hours=data.duration_hours,
        default_start_offset_days=data.default_start_offset_days,
        default_deadline_offset_days=data.default_deadline_offset_days,
    )
    result = await service.create(path)
    return PathTemplateResponse.model_validate(result.model_dump())


@router.get("/{path_id}", dependencies=[Depends(get_optional_user)])
@inject
async def get_path(
    path_id: int,
    service: Annotated[PathTemplateService, Depends(Provide["path_template_service"])],
) -> PathTemplateWithStepsResponse:
    result = await service.get(path_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path template not found",
        )

    return PathTemplateWithStepsResponse.model_validate(result.model_dump())


@router.put("/{path_id}", dependencies=[Depends(require_permissions("path_template.update"))])
@inject
async def update_path(
    path_id: int,
    data: PathTemplateUpdate,
    service: Annotated[PathTemplateService, Depends(Provide["path_template_service"])],
) -> PathTemplateResponse:
    path = PathTemplate(
        name=data.name,
        description=data.description,
        duration_hours=data.duration_hours,
        default_start_offset_days=data.default_start_offset_days,
        default_deadline_offset_days=data.default_deadline_offset_days,
    )
    result = await service.update(path_id, path)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path template not found",
        )

    return PathTemplateResponse.model_validate(result.model_dump())


@router.delete("/{path_id}", dependencies=[Depends(require_permissions("path_template.update"))])
@inject
async def delete_path(
    path_id: int,
    service: Annotated[PathTemplateService, Depends(Provide["path_template_service"])],
) -> MessageResponse:
    success = await service.delete(path_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path template not found",
        )

    return MessageResponse(message="Path template deleted successfully.")

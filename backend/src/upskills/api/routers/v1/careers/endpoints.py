from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from upskills.api.dependencies import get_optional_user, require_permissions
from upskills.api.schemas import MessageResponse, PaginatedResponse
from upskills.domain import Career
from upskills.services import CareerService

from .schemas import (
    CareerCreate,
    CareerResponse,
    CareerUpdate,
    CareerWithPathsResponse,
)

router = APIRouter(prefix="/careers", tags=["Careers"])


@router.get("", dependencies=[Depends(get_optional_user)])
@inject
async def list_careers(
    service: Annotated[CareerService, Depends(Provide["career_service"])],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[CareerResponse]:
    skip = (page - 1) * page_size

    careers, total = await service.get_all(skip=skip, limit=page_size)
    total_pages = (total + page_size - 1) // page_size

    items = [CareerResponse.model_validate(c.model_dump()) for c in careers]

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions("career.create"))],
)
@inject
async def create_career(
    data: CareerCreate,
    service: Annotated[CareerService, Depends(Provide["career_service"])],
) -> CareerResponse:
    career = Career(name=data.name, specialization=data.specialization)
    result = await service.create(career)
    return CareerResponse.model_validate(result.model_dump())


@router.get("/{career_id}", dependencies=[Depends(get_optional_user)])
@inject
async def get_career(
    career_id: int,
    service: Annotated[CareerService, Depends(Provide["career_service"])],
) -> CareerWithPathsResponse:
    result = await service.get(career_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career not found",
        )

    return CareerWithPathsResponse.model_validate(result.model_dump())


@router.put("/{career_id}", dependencies=[Depends(require_permissions("career.update"))])
@inject
async def update_career(
    career_id: int,
    data: CareerUpdate,
    service: Annotated[CareerService, Depends(Provide["career_service"])],
) -> CareerResponse:
    career = Career(name=data.name, specialization=data.specialization)
    result = await service.update(career_id, career)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career not found",
        )

    return CareerResponse.model_validate(result.model_dump())


@router.delete("/{career_id}", dependencies=[Depends(require_permissions("career.update"))])
@inject
async def delete_career(
    career_id: int,
    service: Annotated[CareerService, Depends(Provide["career_service"])],
) -> MessageResponse:
    success = await service.delete(career_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career not found",
        )

    return MessageResponse(message="Career deleted successfully.")

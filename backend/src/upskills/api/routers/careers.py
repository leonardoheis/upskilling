"""Careers router."""

from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from upskills.core.dependencies import CurrentUser, require_permissions
from upskills.models.db.user import User
from upskills.models.domain.base import MessageResponse, PaginatedResponse
from upskills.models.domain.career import (
    CareerCreate,
    CareerResponse,
    CareerUpdate,
    CareerWithPathsResponse,
)
from upskills.services.career import CareerService

router = APIRouter()


@router.get("")
@inject
async def list_careers(
    service: Annotated[CareerService, Depends(Provide["career_service"])],
    current_user: CurrentUser,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[CareerResponse]:
    """List all careers."""
    skip = (page - 1) * page_size

    careers, total = await service.get_all_careers(skip=skip, limit=page_size)
    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=careers,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_career(
    data: CareerCreate,
    service: Annotated[CareerService, Depends(Provide["career_service"])],
    _: Annotated[User, Depends(require_permissions("career.create"))],
) -> CareerResponse:
    """Create a new career (requires career.create permission)."""
    result = await service.create_career(
        name=data.name,
        specialization=data.specialization,
    )
    return result


@router.get("/{career_id}")
@inject
async def get_career(
    career_id: int,
    service: Annotated[CareerService, Depends(Provide["career_service"])],
    current_user: CurrentUser,
) -> CareerWithPathsResponse:
    """Get a specific career with its paths."""
    result = await service.get_career(career_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career not found",
        )

    return result


@router.put("/{career_id}")
@inject
async def update_career(
    career_id: int,
    data: CareerUpdate,
    service: Annotated[CareerService, Depends(Provide["career_service"])],
    _: Annotated[User, Depends(require_permissions("career.update"))],
) -> CareerResponse:
    """Update a career (requires career.update permission)."""
    result = await service.update_career(
        career_id,
        name=data.name,
        specialization=data.specialization,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career not found",
        )

    return result


@router.delete("/{career_id}")
@inject
async def delete_career(
    career_id: int,
    service: Annotated[CareerService, Depends(Provide["career_service"])],
    _: Annotated[User, Depends(require_permissions("career.update"))],
) -> MessageResponse:
    """Delete a career (requires career.update permission)."""
    success = await service.delete_career(career_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career not found",
        )

    return MessageResponse(message="Career deleted successfully.")

"""Logbook router."""

from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from upskills.core.dependencies import CurrentUser, require_permissions
from upskills.models.db.user import User
from upskills.models.domain.base import MessageResponse
from upskills.models.domain.progress import (
    LogEntryCreate,
    LogEntryCreateInput,
    LogEntryDetailResponse,
    LogEntryResponse,
    LogEntryUpdate,
)
from upskills.services.logbook import LogbookService

router = APIRouter()


@router.get("/career-path/{career_path_id}")
@inject
async def get_logbook_entries(
    career_path_id: int,
    current_user: CurrentUser,
    service: Annotated[LogbookService, Depends(Provide["logbook_service"])],
    entry_type: str | None = None,
) -> list[LogEntryDetailResponse]:
    """Get logbook entries for a career path."""
    return await service.get_entries_for_career_path(career_path_id, entry_type)


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_logbook_entry(
    data: LogEntryCreate,
    service: Annotated[LogbookService, Depends(Provide["logbook_service"])],
    _: Annotated[User, Depends(require_permissions("logbook.create"))],
) -> LogEntryResponse:
    """Create a new logbook entry (requires logbook.create permission)."""

    try:
        input_data = LogEntryCreateInput(
            user_id=data.user_id,
            user_career_path_id=data.user_career_path_id,
            entry_type=data.entry_type.value,
            entry_date=data.entry_date,
            notes=data.notes,
            related_user_path_assignment_id=data.related_user_path_assignment_id,
        )
        result = await service.create_entry(input_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/{log_entry_id}")
@inject
async def get_logbook_entry(
    log_entry_id: int,
    current_user: CurrentUser,
    service: Annotated[LogbookService, Depends(Provide["logbook_service"])],
) -> LogEntryDetailResponse:
    """Get a specific logbook entry."""
    result = await service.get_entry(log_entry_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log entry not found",
        )

    return result


@router.put("/{log_entry_id}")
@inject
async def update_logbook_entry(
    log_entry_id: int,
    data: LogEntryUpdate,
    service: Annotated[LogbookService, Depends(Provide["logbook_service"])],
    _: Annotated[User, Depends(require_permissions("logbook.create"))],
) -> LogEntryResponse:
    """Update a logbook entry (requires logbook.create permission)."""
    result = await service.update_entry(
        log_entry_id,
        entry_type=data.entry_type.value if data.entry_type else None,
        entry_date=data.entry_date,
        notes=data.notes,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log entry not found",
        )

    return result


@router.delete("/{log_entry_id}")
@inject
async def delete_logbook_entry(
    log_entry_id: int,
    service: Annotated[LogbookService, Depends(Provide["logbook_service"])],
    _: Annotated[User, Depends(require_permissions("logbook.create"))],
) -> MessageResponse:
    """Delete a logbook entry (requires logbook.create permission)."""
    success = await service.delete_entry(log_entry_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log entry not found",
        )

    return MessageResponse(message="Log entry deleted successfully.")

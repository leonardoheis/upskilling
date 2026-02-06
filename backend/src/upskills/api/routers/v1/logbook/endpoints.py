from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from upskills.api.dependencies import get_optional_user, require_permissions
from upskills.api.schemas import MessageResponse
from upskills.domain import LogEntry
from upskills.services import LogbookService

from .schemas import (
    LogEntryCreate,
    LogEntryDetailResponse,
    LogEntryResponse,
    LogEntryUpdate,
)

router = APIRouter(prefix="/logbook", tags=["Logbook"])


@router.get("/career-path/{career_path_id}", dependencies=[Depends(get_optional_user)])
@inject
async def get_logbook_entries(
    career_path_id: int,
    service: Annotated[LogbookService, Depends(Provide["logbook_service"])],
    entry_type: str | None = None,
) -> list[LogEntryDetailResponse]:
    results = await service.get_entries_for_career_path(career_path_id, entry_type)
    return [LogEntryDetailResponse.model_validate(r.model_dump()) for r in results]


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions("logbook.create"))])
@inject
async def create_logbook_entry(
    data: LogEntryCreate,
    service: Annotated[LogbookService, Depends(Provide["logbook_service"])],
) -> LogEntryResponse:
    entry = LogEntry(
        user_id=data.user_id,
        user_career_path_id=data.user_career_path_id,
        entry_type=data.entry_type.value,
        entry_date=data.entry_date,
        notes=data.notes,
        related_user_path_assignment_id=data.related_user_path_assignment_id,
    )
    result = await service.create_entry(entry)
    return LogEntryResponse.model_validate(result.model_dump())


@router.get("/{log_entry_id}", dependencies=[Depends(get_optional_user)])
@inject
async def get_logbook_entry(
    log_entry_id: int,
    service: Annotated[LogbookService, Depends(Provide["logbook_service"])],
) -> LogEntryDetailResponse:
    result = await service.get_entry(log_entry_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log entry not found",
        )

    return LogEntryDetailResponse.model_validate(result.model_dump())


@router.put("/{log_entry_id}", dependencies=[Depends(require_permissions("logbook.create"))])
@inject
async def update_logbook_entry(
    log_entry_id: int,
    data: LogEntryUpdate,
    service: Annotated[LogbookService, Depends(Provide["logbook_service"])],
) -> LogEntryResponse:
    entry = LogEntry(
        entry_type=data.entry_type.value if data.entry_type else None,
        entry_date=data.entry_date,
        notes=data.notes,
    )
    result = await service.update_entry(log_entry_id, entry)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log entry not found",
        )

    return LogEntryResponse.model_validate(result.model_dump())


@router.delete("/{log_entry_id}", dependencies=[Depends(require_permissions("logbook.create"))])
@inject
async def delete_logbook_entry(
    log_entry_id: int,
    service: Annotated[LogbookService, Depends(Provide["logbook_service"])],
) -> MessageResponse:
    success = await service.delete_entry(log_entry_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log entry not found",
        )

    return MessageResponse(message="Log entry deleted successfully.")

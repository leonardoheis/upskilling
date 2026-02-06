from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from upskills.api.dependencies import authenticated, require_permissions
from upskills.api.schemas import MessageResponse, PaginatedResponse
from upskills.domain import Team, User
from upskills.services import TeamService

from .schemas import (
    TeamCreate,
    TeamListResponse,
    TeamMemberAdd,
    TeamMemberBulkAdd,
    TeamMemberResponse,
    TeamResponse,
    TeamUpdate,
    TeamWithMembersResponse,
)

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("", dependencies=[Depends(require_permissions("team.view"))])
@inject
async def list_teams(
    service: Annotated[TeamService, Depends(Provide["team_service"])],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[TeamListResponse]:
    skip = (page - 1) * page_size
    teams, total = await service.get_all_teams(skip=skip, limit=page_size)
    total_pages = (total + page_size - 1) // page_size

    items = [TeamListResponse.model_validate(t.model_dump()) for t in teams]

    return PaginatedResponse[TeamListResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/my-teams")
@inject
async def get_my_managed_teams(
    service: Annotated[TeamService, Depends(Provide["team_service"])],
    current_user: Annotated[User, Depends(authenticated)],
) -> list[TeamWithMembersResponse]:
    teams = await service.get_teams_by_manager(current_user.user_id)
    return [TeamWithMembersResponse.model_validate(t.model_dump()) for t in teams]


@router.get("/member-of")
@inject
async def get_teams_im_member_of(
    service: Annotated[TeamService, Depends(Provide["team_service"])],
    current_user: Annotated[User, Depends(authenticated)],
) -> list[TeamResponse]:
    teams = await service.get_teams_for_user(current_user.user_id)
    return [TeamResponse.model_validate(t.model_dump()) for t in teams]


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions("team.manage"))])
@inject
async def create_team(
    data: TeamCreate,
    service: Annotated[TeamService, Depends(Provide["team_service"])],
) -> TeamWithMembersResponse:
    team = Team(name=data.name, manager_user_id=data.manager_user_id)
    result = await service.create_team(team)
    return TeamWithMembersResponse.model_validate(result.model_dump())


@router.get("/{team_id}", dependencies=[Depends(require_permissions("team.view"))])
@inject
async def get_team(
    team_id: int,
    service: Annotated[TeamService, Depends(Provide["team_service"])],
) -> TeamWithMembersResponse:
    result = await service.get_team(team_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    return TeamWithMembersResponse.model_validate(result.model_dump())


@router.put("/{team_id}", dependencies=[Depends(require_permissions("team.manage"))])
@inject
async def update_team(
    team_id: int,
    data: TeamUpdate,
    service: Annotated[TeamService, Depends(Provide["team_service"])],
) -> TeamWithMembersResponse:
    team = Team(name=data.name, manager_user_id=data.manager_user_id)
    result = await service.update_team(team_id, team)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    return TeamWithMembersResponse.model_validate(result.model_dump())


@router.delete("/{team_id}", dependencies=[Depends(require_permissions("team.manage"))])
@inject
async def delete_team(
    team_id: int,
    service: Annotated[TeamService, Depends(Provide["team_service"])],
) -> MessageResponse:
    success = await service.delete_team(team_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    return MessageResponse(message="Team deleted successfully.")


@router.get("/{team_id}/members", dependencies=[Depends(require_permissions("team.view"))])
@inject
async def get_team_members(
    team_id: int,
    service: Annotated[TeamService, Depends(Provide["team_service"])],
) -> list[TeamMemberResponse]:
    members = await service.get_team_members(team_id)
    return [TeamMemberResponse.model_validate(m.model_dump()) for m in members]


@router.post("/{team_id}/members", dependencies=[Depends(require_permissions("team.manage"))])
@inject
async def add_team_member(
    team_id: int,
    data: TeamMemberAdd,
    service: Annotated[TeamService, Depends(Provide["team_service"])],
) -> MessageResponse:
    await service.add_member(team_id, data.user_id)
    return MessageResponse(message="Member added to team.")


@router.post("/{team_id}/members/bulk", dependencies=[Depends(require_permissions("team.manage"))])
@inject
async def add_team_members_bulk(
    team_id: int,
    data: TeamMemberBulkAdd,
    service: Annotated[TeamService, Depends(Provide["team_service"])],
) -> MessageResponse:
    errors = []

    for user_id in data.user_ids:
        try:
            await service.add_member(team_id, user_id)
        except ValueError as e:
            errors.append(f"User {user_id}: {e!s}")

    if errors:
        return MessageResponse(
            message=f"Added {len(data.user_ids) - len(errors)} members.",
            detail="; ".join(errors),
        )

    return MessageResponse(message=f"Added {len(data.user_ids)} members to team.")


@router.delete("/{team_id}/members/{user_id}", dependencies=[Depends(require_permissions("team.manage"))])
@inject
async def remove_team_member(
    team_id: int,
    user_id: int,
    service: Annotated[TeamService, Depends(Provide["team_service"])],
) -> MessageResponse:
    success = await service.remove_member(team_id, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in team",
        )

    return MessageResponse(message="Member removed from team.")

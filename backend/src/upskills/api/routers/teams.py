"""Teams router."""

from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from upskills.core.dependencies import CurrentUser, require_permissions
from upskills.models.db.user import User
from upskills.models.domain.base import MessageResponse, PaginatedResponse
from upskills.models.domain.team import (
    TeamCreate,
    TeamListResponse,
    TeamMemberAdd,
    TeamMemberBulkAdd,
    TeamMemberResponse,
    TeamResponse,
    TeamUpdate,
    TeamWithMembersResponse,
)
from upskills.services.team import TeamService

router = APIRouter()


@router.get("")
@inject
async def list_teams(
    service: Annotated[TeamService, Depends(Provide["team_service"])],
    _: Annotated[User, Depends(require_permissions("team.view"))],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[TeamListResponse]:
    """List all teams (requires team.view permission)."""
    skip = (page - 1) * page_size

    teams, total = await service.get_all_teams(skip=skip, limit=page_size)
    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=teams,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/my-teams")
@inject
async def get_my_managed_teams(
    service: Annotated[TeamService, Depends(Provide["team_service"])],
    current_user: CurrentUser,
) -> list[TeamWithMembersResponse]:
    """Get teams managed by the current user."""
    return await service.get_teams_by_manager(current_user.user_id)


@router.get("/member-of")
@inject
async def get_teams_im_member_of(
    service: Annotated[TeamService, Depends(Provide["team_service"])],
    current_user: CurrentUser,
) -> list[TeamResponse]:
    """Get teams the current user is a member of."""
    return await service.get_teams_for_user(current_user.user_id)


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_team(
    data: TeamCreate,
    service: Annotated[TeamService, Depends(Provide["team_service"])],
    _: Annotated[User, Depends(require_permissions("team.manage"))],
) -> TeamWithMembersResponse:
    """Create a new team (requires team.manage permission)."""

    try:
        result = await service.create_team(
            name=data.name,
            manager_user_id=data.manager_user_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/{team_id}")
@inject
async def get_team(
    team_id: int,
    service: Annotated[TeamService, Depends(Provide["team_service"])],
    _: Annotated[User, Depends(require_permissions("team.view"))],
) -> TeamWithMembersResponse:
    """Get a specific team (requires team.view permission)."""
    result = await service.get_team(team_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    return result


@router.put("/{team_id}")
@inject
async def update_team(
    team_id: int,
    data: TeamUpdate,
    service: Annotated[TeamService, Depends(Provide["team_service"])],
    _: Annotated[User, Depends(require_permissions("team.manage"))],
) -> TeamWithMembersResponse:
    """Update a team (requires team.manage permission)."""

    try:
        result = await service.update_team(
            team_id,
            name=data.name,
            manager_user_id=data.manager_user_id,
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found",
            )

        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete("/{team_id}")
@inject
async def delete_team(
    team_id: int,
    service: Annotated[TeamService, Depends(Provide["team_service"])],
    _: Annotated[User, Depends(require_permissions("team.manage"))],
) -> MessageResponse:
    """Delete a team (requires team.manage permission)."""
    success = await service.delete_team(team_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    return MessageResponse(message="Team deleted successfully.")


@router.get("/{team_id}/members")
@inject
async def get_team_members(
    team_id: int,
    service: Annotated[TeamService, Depends(Provide["team_service"])],
    _: Annotated[User, Depends(require_permissions("team.view"))],
) -> list[TeamMemberResponse]:
    """Get members of a team (requires team.view permission)."""
    return await service.get_team_members(team_id)


@router.post("/{team_id}/members")
@inject
async def add_team_member(
    team_id: int,
    data: TeamMemberAdd,
    service: Annotated[TeamService, Depends(Provide["team_service"])],
    _: Annotated[User, Depends(require_permissions("team.manage"))],
) -> MessageResponse:
    """Add a member to a team (requires team.manage permission)."""

    try:
        await service.add_member(team_id, data.user_id)
        return MessageResponse(message="Member added to team.")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post("/{team_id}/members/bulk")
@inject
async def add_team_members_bulk(
    team_id: int,
    data: TeamMemberBulkAdd,
    service: Annotated[TeamService, Depends(Provide["team_service"])],
    _: Annotated[User, Depends(require_permissions("team.manage"))],
) -> MessageResponse:
    """Add multiple members to a team (requires team.manage permission)."""
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


@router.delete("/{team_id}/members/{user_id}")
@inject
async def remove_team_member(
    team_id: int,
    user_id: int,
    service: Annotated[TeamService, Depends(Provide["team_service"])],
    _: Annotated[User, Depends(require_permissions("team.manage"))],
) -> MessageResponse:
    """Remove a member from a team (requires team.manage permission)."""
    success = await service.remove_member(team_id, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in team",
        )

    return MessageResponse(message="Member removed from team.")

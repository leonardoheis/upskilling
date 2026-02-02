"""Users router."""

from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from upskills.core.dependencies import CurrentUser, require_permissions
from upskills.models.db.user import User
from upskills.models.domain.base import MessageResponse, PaginatedResponse
from upskills.models.domain.user import (
    PasswordChange,
    UserResponse,
    UserUpdate,
    UserWithPermissions,
)
from upskills.services.user import UserService

router = APIRouter()


@router.get("")
@inject
async def list_users(
    service: Annotated[UserService, Depends(Provide["user_service"])],
    _: Annotated[User, Depends(require_permissions("team.view"))],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[UserResponse]:
    """List all users (requires team.view permission)."""
    skip = (page - 1) * page_size

    users, total = await service.get_all_users(skip=skip, limit=page_size)
    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=users,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/me")
@inject
async def get_my_profile(
    service: Annotated[UserService, Depends(Provide["user_service"])],
    current_user: CurrentUser,
) -> UserWithPermissions:
    """Get current user's profile with permissions."""
    result = await service.get_user_with_permissions(current_user.user_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return result


@router.put("/me")
@inject
async def update_my_profile(
    data: UserUpdate,
    service: Annotated[UserService, Depends(Provide["user_service"])],
    current_user: CurrentUser,
) -> UserResponse:
    """Update current user's profile."""
    try:
        result = await service.update_user(
            current_user.user_id,
            full_name=data.full_name,
            email=data.email,
            bio=data.bio,
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post("/me/change-password")
@inject
async def change_my_password(
    data: PasswordChange,
    service: Annotated[UserService, Depends(Provide["user_service"])],
    current_user: CurrentUser,
) -> MessageResponse:
    """Change current user's password."""
    try:
        success = await service.change_password(
            current_user.user_id,
            data.current_password,
            data.new_password,
        )

        if success:
            return MessageResponse(message="Password changed successfully.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password.",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/{user_id}")
@inject
async def get_user(
    user_id: int,
    service: Annotated[UserService, Depends(Provide["user_service"])],
    _: Annotated[User, Depends(require_permissions("team.view"))],
) -> UserResponse:
    """Get a specific user (requires team.view permission)."""
    result = await service.get_user(user_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return result


@router.delete("/{user_id}")
@inject
async def delete_user(
    user_id: int,
    service: Annotated[UserService, Depends(Provide["user_service"])],
    _: Annotated[User, Depends(require_permissions("team.manage"))],
) -> MessageResponse:
    """Delete a user (requires team.manage permission).

    User cannot be deleted if they are a member of a team or have career paths assigned.
    """
    try:
        success = await service.delete_user(user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return MessageResponse(message="User deleted successfully.")


@router.post("/{user_id}/roles/{role_name}")
@inject
async def assign_role_to_user(
    user_id: int,
    role_name: str,
    service: Annotated[UserService, Depends(Provide["user_service"])],
    _: Annotated[User, Depends(require_permissions("team.manage"))],
) -> MessageResponse:
    """Assign a role to a user (requires team.manage permission)."""
    try:
        await service.assign_role(user_id, role_name)
        return MessageResponse(message=f"Role '{role_name}' assigned to user.")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete("/{user_id}/roles/{role_name}")
@inject
async def remove_role_from_user(
    user_id: int,
    role_name: str,
    service: Annotated[UserService, Depends(Provide["user_service"])],
    _: Annotated[User, Depends(require_permissions("team.manage"))],
) -> MessageResponse:
    """Remove a role from a user (requires team.manage permission)."""
    try:
        await service.remove_role(user_id, role_name)
        return MessageResponse(message=f"Role '{role_name}' removed from user.")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

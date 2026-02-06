from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from upskills.api.dependencies import authenticated, require_permissions
from upskills.api.schemas import MessageResponse, PaginatedResponse, UserResponse, UserWithPermissionsResponse
from upskills.domain import User as UserDomain
from upskills.services import UserService

from .schemas import PasswordChange, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", dependencies=[Depends(require_permissions("user.view"))])
@inject
async def list_users(
    service: Annotated[UserService, Depends(Provide["user_service"])],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[UserResponse]:
    skip = (page - 1) * page_size
    users, total = await service.get_all_users(skip=skip, limit=page_size)
    total_pages = (total + page_size - 1) // page_size

    items = [UserResponse.model_validate(u.model_dump()) for u in users]

    return PaginatedResponse[UserResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/me")
@inject
async def get_my_profile(
    service: Annotated[UserService, Depends(Provide["user_service"])],
    current_user: Annotated[UserDomain, Depends(authenticated)],
) -> UserWithPermissionsResponse:
    result = await service.get_user_with_permissions(current_user.user_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserWithPermissionsResponse.model_validate(result.model_dump())


@router.put("/me")
@inject
async def update_my_profile(
    data: UserUpdate,
    service: Annotated[UserService, Depends(Provide["user_service"])],
    current_user: Annotated[UserDomain, Depends(authenticated)],
) -> UserResponse:
    user = UserDomain(
        full_name=data.full_name,
        email=data.email,
        bio=data.bio,
    )
    result = await service.update_user(current_user.user_id, user)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(result.model_dump())


@router.post("/me/change-password")
@inject
async def change_my_password(
    data: PasswordChange,
    service: Annotated[UserService, Depends(Provide["user_service"])],
    current_user: Annotated[UserDomain, Depends(authenticated)],
) -> MessageResponse:
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


@router.get("/{user_id}", dependencies=[Depends(require_permissions("user.view"))])
@inject
async def get_user(
    user_id: int,
    service: Annotated[UserService, Depends(Provide["user_service"])],
) -> UserResponse:
    result = await service.get_user(user_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(result.model_dump())


@router.delete("/{user_id}", dependencies=[Depends(require_permissions("user.manage"))])
@inject
async def delete_user(
    user_id: int,
    service: Annotated[UserService, Depends(Provide["user_service"])],
) -> MessageResponse:
    success = await service.delete_user(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return MessageResponse(message="User deleted successfully.")


@router.post("/{user_id}/roles/{role_name}", dependencies=[Depends(require_permissions("user.manage"))])
@inject
async def assign_role_to_user(
    user_id: int,
    role_name: str,
    service: Annotated[UserService, Depends(Provide["user_service"])],
) -> MessageResponse:
    await service.assign_role(user_id, role_name)
    return MessageResponse(message=f"Role '{role_name}' assigned to user.")


@router.delete("/{user_id}/roles/{role_name}", dependencies=[Depends(require_permissions("user.manage"))])
@inject
async def remove_role_from_user(
    user_id: int,
    role_name: str,
    service: Annotated[UserService, Depends(Provide["user_service"])],
) -> MessageResponse:
    await service.remove_role(user_id, role_name)
    return MessageResponse(message=f"Role '{role_name}' removed from user.")

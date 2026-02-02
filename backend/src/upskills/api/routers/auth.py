"""Authentication router."""

from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from upskills.core.dependencies import CurrentUser
from upskills.models.domain.auth import (
    AuthResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from upskills.models.domain.base import MessageResponse
from upskills.models.domain.user import (
    PasswordReset,
    PasswordResetRequest,
    UserResponse,
)
from upskills.services.auth import AuthService

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
@inject
async def register(
    data: RegisterRequest,
    service: Annotated[AuthService, Depends(Provide["auth_service"])],
) -> AuthResponse:
    """Register a new user account."""
    try:
        return await service.register(
            full_name=data.full_name,
            email=data.email,
            password=data.password,
            bio=data.bio,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post("/login")
@inject
async def login(
    data: LoginRequest,
    service: Annotated[AuthService, Depends(Provide["auth_service"])],
) -> AuthResponse:
    """Authenticate and get access tokens."""
    try:
        return await service.login(data.email, data.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e


@router.post("/refresh")
@inject
async def refresh_tokens(
    data: RefreshTokenRequest,
    service: Annotated[AuthService, Depends(Provide["auth_service"])],
) -> TokenResponse:
    """Refresh access and refresh tokens."""
    try:
        return await service.refresh_tokens(data.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e


@router.post("/password-reset-request")
@inject
async def request_password_reset(
    data: PasswordResetRequest,
    service: Annotated[AuthService, Depends(Provide["auth_service"])],
) -> MessageResponse:
    """Request a password reset email."""
    token = await service.request_password_reset(data.email)

    # In production, send email with token
    # For now, return success regardless (don't reveal if email exists)
    if token:
        # Log or send email with token
        # In a real app: send_password_reset_email(data.email, token)
        pass

    return MessageResponse(
        message="If the email exists, a password reset link has been sent.",
    )


@router.post("/password-reset")
@inject
async def reset_password(
    data: PasswordReset,
    service: Annotated[AuthService, Depends(Provide["auth_service"])],
) -> MessageResponse:
    """Reset password using a reset token."""
    try:
        success = await service.reset_password(data.token, data.new_password)

        if success:
            return MessageResponse(message="Password has been reset successfully.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to reset password.",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/me")
async def get_current_user_info(
    current_user: CurrentUser,
) -> UserResponse:
    """Get the current authenticated user's information."""
    from upskills.models.domain.user import RoleResponse

    roles: list[RoleResponse] = []
    if current_user.roles:
        roles.extend(
            RoleResponse(
                role_id=user_role.role.role_id,
                name=user_role.role.name,
                description=user_role.role.description,
                max_active_paths=user_role.role.max_active_paths,
            )
            for user_role in current_user.roles
            if user_role.role
        )

    return UserResponse(
        user_id=current_user.user_id,
        full_name=current_user.full_name,
        email=current_user.email,
        bio=current_user.bio,
        created_at=current_user.created_at,
        roles=roles,
    )

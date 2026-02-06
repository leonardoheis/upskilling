from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from upskills.api.dependencies import authenticated
from upskills.api.schemas import MessageResponse, UserResponse
from upskills.domain import User
from upskills.services import AuthService

from .schemas import (
    AuthResponse,
    LoginRequest,
    PasswordReset,
    PasswordResetRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
@inject
async def register(
    data: RegisterRequest,
    service: Annotated[AuthService, Depends(Provide["auth_service"])],
) -> AuthResponse:
    result = await service.register(
        full_name=data.full_name,
        email=data.email,
        password=data.password,
        bio=data.bio,
    )
    return AuthResponse(
        user=UserResponse.model_validate(result.user.model_dump()),
        tokens=TokenResponse.model_validate(result.tokens.model_dump()),
    )


@router.post("/login")
@inject
async def login(
    data: LoginRequest,
    service: Annotated[AuthService, Depends(Provide["auth_service"])],
) -> AuthResponse:
    try:
        result = await service.login(data.email, data.password)
        return AuthResponse(
            user=UserResponse.model_validate(result.user.model_dump()),
            tokens=TokenResponse.model_validate(result.tokens.model_dump()),
        )
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
    try:
        result = await service.refresh_tokens(data.refresh_token)
        return TokenResponse.model_validate(result.model_dump())
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
    token = await service.request_password_reset(data.email)
    if token:
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
    try:
        success = await service.reset_password(data.token, data.new_password)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reset password.",
            )

        return MessageResponse(message="Password has been reset successfully.")

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/me")
async def get_current_user_info(
    current_user: Annotated[User, Depends(authenticated)],
) -> UserResponse:
    return UserResponse.model_validate(current_user.model_dump())

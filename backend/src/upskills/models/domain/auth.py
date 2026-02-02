"""Authentication Pydantic domain models."""

from pydantic import EmailStr, Field

from upskills.models.domain.base import DomainModel
from upskills.models.domain.user import UserResponse


class LoginRequest(DomainModel):
    """Request model for login."""

    email: EmailStr
    password: str


class RegisterRequest(DomainModel):
    """Request model for user registration."""

    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    bio: str | None = None


class TokenResponse(DomainModel):
    """Response model for authentication tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(DomainModel):
    """JWT token payload model."""

    sub: str  # user_id as string
    exp: int  # expiration timestamp
    type: str  # "access" or "refresh"


class RefreshTokenRequest(DomainModel):
    """Request model for refreshing tokens."""

    refresh_token: str


class AuthResponse(DomainModel):
    """Full authentication response with user and tokens."""

    user: UserResponse
    tokens: TokenResponse

from pydantic import EmailStr, Field

from upskills.api.schemas import BaseSchema, UserResponse
from upskills.domain import TokenType


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str


class RegisterRequest(BaseSchema):
    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    bio: str | None = None


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: TokenType = TokenType.BEARER


class RefreshTokenRequest(BaseSchema):
    refresh_token: str


class AuthResponse(BaseSchema):
    user: UserResponse
    tokens: TokenResponse


class PasswordResetRequest(BaseSchema):
    email: EmailStr


class PasswordReset(BaseSchema):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

from enum import StrEnum

from .base import DomainModel
from .user import User as UserDomain


class TokenType(StrEnum):
    BEARER = "bearer"


class Token(DomainModel):
    access_token: str
    refresh_token: str
    token_type: TokenType = TokenType.BEARER


class AuthResult(DomainModel):
    user: UserDomain
    tokens: Token


class TokenPayload(DomainModel):
    sub: str
    type: str
    exp: int

"""Security utilities for authentication and authorization."""

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from upskills.core.config import get_settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token."""
    settings = get_settings()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "type": "access",
    }

    encoded: str = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded


def create_refresh_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT refresh token."""
    settings = get_settings()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)

    to_encode: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh",
    }

    encoded: str = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded


def decode_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a JWT token."""
    settings = get_settings()

    try:
        payload: dict[str, Any] = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> str | None:
    """Verify a token and return the subject (user_id) if valid."""
    payload = decode_token(token)

    if payload is None:
        return None

    if payload.get("type") != token_type:
        return None

    exp = payload.get("exp")
    if exp and datetime.fromtimestamp(exp, tz=UTC) < datetime.now(UTC):
        return None

    return payload.get("sub")

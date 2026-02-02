"""FastAPI dependencies for authentication and authorization."""

from collections.abc import Callable, Coroutine
from typing import Annotated, Any

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from upskills.core.security import verify_token
from upskills.models.db.user import User
from upskills.repositories.user import UserRepository

# Security scheme
security = HTTPBearer()


@inject
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    repo: Annotated[UserRepository, Depends(Provide["user_repository"])],
) -> User:
    """Get the current authenticated user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    user_id_str = verify_token(token, "access")

    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception from None

    user = await repo.get_by_id(user_id)

    if user is None:
        raise credentials_exception

    return user


@inject
async def get_current_user_optional(
    request: Request,
    repo: Annotated[UserRepository, Depends(Provide["user_repository"])],
) -> User | None:
    """Get the current user if authenticated, otherwise None."""
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    user_id_str = verify_token(token, "access")

    if user_id_str is None:
        return None

    try:
        user_id = int(user_id_str)
    except ValueError:
        return None

    return await repo.get_by_id(user_id)


def require_permissions(
    *required_permissions: str,
) -> Callable[..., Coroutine[Any, Any, User]]:
    """Dependency factory that checks if user has required permissions."""

    @inject
    async def check_permissions(
        current_user: Annotated[User, Depends(get_current_user)],
        repo: Annotated[UserRepository, Depends(Provide["user_repository"])],
    ) -> User:
        user_permissions = await repo.get_user_permissions(current_user.user_id)

        for permission in required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required: {permission}",
                )

        return current_user

    return check_permissions


# Type aliases for common dependencies
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_current_user_optional)]

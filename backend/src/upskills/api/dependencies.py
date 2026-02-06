"""FastAPI dependencies for authentication and authorization."""

from collections.abc import Callable, Coroutine
from typing import Annotated, Any

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from upskills.core.security import verify_token
from upskills.repositories import User, UserRepository

security = HTTPBearer()


@inject
async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user_repository: Annotated[UserRepository, Depends(Provide["user_repository"])],
) -> User | None:
    if credentials is None or user_repository is None:
        return None

    token = credentials.credentials
    user_id_str = verify_token(token, "access")

    if user_id_str is None:
        return None

    user_id = int(user_id_str)
    return await user_repository.get_by_id(user_id)


CurrentUser = Annotated[User | None, Depends(get_optional_user)]


def authenticated(
    user: CurrentUser,
) -> User:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not find sub claim in token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_permissions(
    *required_permissions: str,
) -> Callable[..., Coroutine[Any, Any, User]]:
    @inject
    async def check_permissions(
        current_user: Annotated[User, Depends(authenticated)],
        user_repository: Annotated[UserRepository, Depends(Provide["user_repository"])],
    ) -> User:
        user_permissions = await user_repository.get_user_permissions(current_user.user_id)

        for permission in required_permissions:
            if permission in user_permissions:
                continue

            message = f"Permission denied. User has permission: {user_permissions} but required: {permission}."
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=message,
            )

        return current_user

    return check_permissions

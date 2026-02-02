"""Authentication service."""

from dependency_injector.wiring import Provide, inject

from upskills.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from upskills.models.db.user import User
from upskills.models.domain.auth import AuthResponse, TokenResponse
from upskills.models.domain.user import RoleResponse, UserResponse
from upskills.repositories.role import RoleRepository
from upskills.repositories.user import UserRepository


class AuthService:
    """Service for authentication operations."""

    @inject
    def __init__(
        self,
        user_repository: UserRepository = Provide["user_repository"],
        role_repository: RoleRepository = Provide["role_repository"],
    ) -> None:
        self._user_repository = user_repository
        self._role_repository = role_repository

    async def register(
        self,
        full_name: str,
        email: str,
        password: str,
        bio: str | None = None,
    ) -> AuthResponse:
        """Register a new user."""
        # Check if email already exists
        existing = await self._user_repository.get_by_email(email)
        if existing:
            msg = "Email already registered"
            raise ValueError(msg)

        # Create user
        user = await self._user_repository.create({
            "full_name": full_name,
            "email": email,
            "password_hash": hash_password(password),
            "bio": bio,
        })

        # Assign default role (mentee)
        mentee_role = await self._role_repository.get_by_name("mentee")
        if mentee_role:
            await self._user_repository.assign_role(user.user_id, mentee_role.role_id)
            # Refresh to get the role
            refreshed_user = await self._user_repository.get_by_id(user.user_id)
            if refreshed_user:
                user = refreshed_user

        # Generate tokens
        tokens = self._create_tokens(user.user_id)

        return AuthResponse(
            user=self._user_to_response(user),
            tokens=tokens,
        )

    async def login(self, email: str, password: str) -> AuthResponse:
        """Authenticate a user and return tokens."""
        user = await self._user_repository.get_by_email(email)

        if not user or not verify_password(password, user.password_hash):
            msg = "Invalid email or password"
            raise ValueError(msg)

        tokens = self._create_tokens(user.user_id)

        return AuthResponse(
            user=self._user_to_response(user),
            tokens=tokens,
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Refresh access and refresh tokens."""
        user_id_str = verify_token(refresh_token, "refresh")

        if user_id_str is None:
            msg = "Invalid or expired refresh token"
            raise ValueError(msg)

        user_id = int(user_id_str)
        user = await self._user_repository.get_by_id(user_id)

        if not user:
            msg = "User not found"
            raise ValueError(msg)

        return self._create_tokens(user.user_id)

    async def request_password_reset(self, email: str) -> str | None:
        """Request a password reset token."""
        user = await self._user_repository.get_by_email(email)

        if not user:
            # Don't reveal whether email exists
            return None

        return await self._user_repository.create_password_reset_token(user.user_id)

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using a reset token."""
        reset_token = await self._user_repository.get_password_reset_token(token)

        if not reset_token:
            msg = "Invalid or expired reset token"
            raise ValueError(msg)

        # Update password
        user = await self._user_repository.get_by_id(reset_token.user_id)
        if user:
            await self._user_repository.update(user, {"password_hash": hash_password(new_password)})
            await self._user_repository.mark_token_used(reset_token)
            return True

        return False

    @staticmethod
    def _create_tokens(user_id: int) -> TokenResponse:
        """Create access and refresh tokens for a user."""
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )

    @staticmethod
    def _user_to_response(user: User) -> UserResponse:
        """Convert a User model to UserResponse."""
        roles: list[RoleResponse] = []
        if user.roles:
            roles.extend(
                RoleResponse(
                    role_id=user_role.role.role_id,
                    name=user_role.role.name,
                    description=user_role.role.description,
                    max_active_paths=user_role.role.max_active_paths,
                )
                for user_role in user.roles
                if user_role.role
            )

        return UserResponse(
            user_id=user.user_id,
            full_name=user.full_name,
            email=user.email,
            bio=user.bio,
            created_at=user.created_at,
            roles=roles,
        )

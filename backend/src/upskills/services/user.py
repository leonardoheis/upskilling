"""User service."""

from dependency_injector.wiring import Provide, inject

from upskills.core.security import hash_password, verify_password
from upskills.models.db.user import User
from upskills.models.domain.user import RoleResponse, UserResponse, UserWithPermissions
from upskills.repositories.role import RoleRepository
from upskills.repositories.user import UserRepository


class UserService:
    """Service for user operations."""

    @inject
    def __init__(
        self,
        user_repository: UserRepository = Provide["user_repository"],
        role_repository: RoleRepository = Provide["role_repository"],
    ) -> None:
        self._user_repository = user_repository
        self._role_repository = role_repository

    async def get_user(self, user_id: int) -> UserResponse | None:
        """Get a user by ID."""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            return None
        return self._user_to_response(user)

    async def get_user_with_permissions(self, user_id: int) -> UserWithPermissions | None:
        """Get a user with their permissions."""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            return None

        permissions = await self._user_repository.get_user_permissions(user_id)

        response = self._user_to_response(user)
        return UserWithPermissions(
            **response.model_dump(),
            permissions=permissions,
        )

    async def get_all_users(
        self, *, skip: int = 0, limit: int = 100
    ) -> tuple[list[UserResponse], int]:
        """Get all users with pagination."""
        users = await self._user_repository.get_all_with_roles(skip=skip, limit=limit)
        total = await self._user_repository.count()
        return [self._user_to_response(u) for u in users], total

    async def update_user(
        self,
        user_id: int,
        full_name: str | None = None,
        email: str | None = None,
        bio: str | None = None,
    ) -> UserResponse | None:
        """Update a user's profile."""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            return None

        # Check email uniqueness if changing
        if email and email != user.email:
            existing = await self._user_repository.get_by_email(email)
            if existing:
                msg = "Email already in use"
                raise ValueError(msg)

        update_data = {}
        if full_name is not None:
            update_data["full_name"] = full_name
        if email is not None:
            update_data["email"] = email
        if bio is not None:
            update_data["bio"] = bio

        if update_data:
            user = await self._user_repository.update(user, update_data)

        return self._user_to_response(user)

    async def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str,
    ) -> bool:
        """Change a user's password."""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            return False

        if not verify_password(current_password, user.password_hash):
            msg = "Current password is incorrect"
            raise ValueError(msg)

        await self._user_repository.update(user, {"password_hash": hash_password(new_password)})
        return True

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user.

        Raises:
            ValueError: If user is part of a team or has career paths assigned.
        """
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            return False

        # Check if user is a member of any team
        if await self._user_repository.has_team_memberships(user_id):
            msg = "Cannot delete user: they are a member of one or more teams. Remove them from all teams first."
            raise ValueError(msg)

        # Check if user has any career paths assigned
        if await self._user_repository.has_career_paths(user_id):
            msg = "Cannot delete user: they have career paths assigned. Remove all career path assignments first."
            raise ValueError(msg)

        await self._user_repository.delete(user)
        return True

    async def assign_role(self, user_id: int, role_name: str) -> bool:
        """Assign a role to a user."""
        role = await self._role_repository.get_by_name(role_name)
        if not role:
            msg = f"Role '{role_name}' not found"
            raise ValueError(msg)

        await self._user_repository.assign_role(user_id, role.role_id)
        return True

    async def remove_role(self, user_id: int, role_name: str) -> bool:
        """Remove a role from a user."""
        role = await self._role_repository.get_by_name(role_name)
        if not role:
            msg = f"Role '{role_name}' not found"
            raise ValueError(msg)

        await self._user_repository.remove_role(user_id, role.role_id)
        return True

    @staticmethod
    def _user_to_response(user: User) -> UserResponse:
        """Convert a User model to UserResponse.

        Args:
            user: The User database model to convert.

        Returns:
            UserResponse: The converted user response object.
        """
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

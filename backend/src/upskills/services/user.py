from dataclasses import dataclass

from dependency_injector.wiring import Provide

from upskills.core import hash_password, verify_password
from upskills.domain import User
from upskills.repositories import RoleRepository, UserRepository


@dataclass
class UserService:
    user_repository: UserRepository = Provide["user_repository"]
    role_repository: RoleRepository = Provide["role_repository"]

    async def get_user(self, user_id: int) -> User | None:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None
        return self.user_repository.to_domain(user)

    async def get_user_with_permissions(self, user_id: int) -> User | None:
        user = await self.user_repository.get_by_id(user_id, id_column="user_id")
        if not user:
            return None

        permissions = await self.user_repository.get_user_permissions(user_id)
        user_domain = self.user_repository.to_domain(user)
        user_domain.permissions = permissions
        return user_domain

    async def get_all_users(self, *, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        users = await self.user_repository.get_all_with_roles(skip=skip, limit=limit)
        total = await self.user_repository.count()
        return [self.user_repository.to_domain(user) for user in users], total

    async def update_user(
        self,
        user_id: int,
        full_name: str | None = None,
        email: str | None = None,
        bio: str | None = None,
    ) -> User | None:
        user = await self.user_repository.get_by_id(user_id, id_column="user_id")
        if not user:
            return None

        if email and email != user.email:
            existing = await self.user_repository.get_by_email(email)
            if existing:
                msg = "Email already in use"
                raise ValueError(msg)

        update_user = {}
        if full_name is not None:
            update_user["full_name"] = full_name
        if email is not None:
            update_user["email"] = email
        if bio is not None:
            update_user["bio"] = bio

        if not update_user:
            return self.user_repository.to_domain(user)

        updated_user = await self.user_repository.update(user, update_user)
        return self.user_repository.to_domain(updated_user)

    async def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str,
    ) -> bool:
        db_model = await self.user_repository.get_by_id(user_id, id_column="user_id")
        if not db_model:
            return False

        if not verify_password(current_password, db_model.password_hash):
            msg = "Current password is incorrect"
            raise ValueError(msg)

        await self.user_repository.update(db_model, {"password_hash": hash_password(new_password)})
        return True

    async def delete_user(self, user_id: int) -> bool:
        db_model = await self.user_repository.get_by_id(user_id, id_column="user_id")
        if not db_model:
            return False

        if await self.user_repository.has_team_memberships(user_id):
            msg = "Cannot delete user: they are a member of one or more teams. Remove them from all teams first."
            raise ValueError(msg)

        if await self.user_repository.has_career_paths(user_id):
            msg = "Cannot delete user: they have career paths assigned. Remove all career path assignments first."
            raise ValueError(msg)

        await self.user_repository.delete(db_model)
        return True

    async def assign_role(self, user_id: int, role_name: str) -> bool:
        role = await self.role_repository.get_by_name(role_name)
        if not role:
            msg = f"Role '{role_name}' not found"
            raise ValueError(msg)

        await self.user_repository.assign_role(user_id, role.role_id)
        return True

    async def remove_role(self, user_id: int, role_name: str) -> bool:
        role = await self.role_repository.get_by_name(role_name)
        if not role:
            msg = f"Role '{role_name}' not found"
            raise ValueError(msg)

        await self.user_repository.remove_role(user_id, role.role_id)
        return True

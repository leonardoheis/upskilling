import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from upskills.domain import User as UserDomain
from upskills.repositories.base import BaseRepository
from upskills.repositories.team.models import TeamMember
from upskills.repositories.user_career_path.models import UserCareerPath

from .models import Action, PasswordResetToken, Role, User, UserRole


class UserRepository(BaseRepository[User]):
    async def get_by_id(self, id_value: int, id_column: str = "user_id") -> User | None:
        async with self._db_provider.session() as session:
            stmt = (
                select(User)
                .options(selectinload(User.roles).selectinload(UserRole.role))
                .where(User.user_id == id_value)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        async with self._db_provider.session() as session:
            stmt = select(User).options(selectinload(User.roles).selectinload(UserRole.role)).where(User.email == email)
            stmt = select(User).options(selectinload(User.roles).selectinload(UserRole.role)).where(User.email == email)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_all_with_roles(self, *, skip: int = 0, limit: int = 100) -> list[User]:
        async with self._db_provider.session() as session:
            stmt = select(User).options(selectinload(User.roles).selectinload(UserRole.role)).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_user_permissions(self, user_id: int) -> list[str]:
        async with self._db_provider.session() as session:
            stmt = (
                select(Action.action_key)
                .join(Action.roles)
                .join(Role)
                .join(Role.users)
                .where(UserRole.user_id == user_id)
                .distinct()
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def assign_role(self, user_id: int, role_id: int) -> None:
        async with self._db_provider.session() as session:
            user_role = UserRole(user_id=user_id, role_id=role_id)
            session.add(user_role)
            await session.flush()
            await session.commit()

    async def remove_role(self, user_id: int, role_id: int) -> None:
        async with self._db_provider.session() as session:
            stmt = select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
            result = await session.execute(stmt)
            user_role = result.scalar_one_or_none()
            if user_role:
                await session.delete(user_role)
                await session.flush()
                await session.commit()

    async def create_password_reset_token(self, user_id: int, expires_hours: int = 24) -> str:
        async with self._db_provider.session() as session:
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now(UTC) + timedelta(hours=expires_hours)

            reset_token = PasswordResetToken(
                user_id=user_id,
                token=token,
                expires_at=expires_at,
            )
            session.add(reset_token)
            await session.flush()
            await session.commit()
            return token

    async def get_password_reset_token(self, token: str) -> PasswordResetToken | None:
        async with self._db_provider.session() as session:
            stmt = select(PasswordResetToken).where(
                PasswordResetToken.token == token,
                PasswordResetToken.used.is_(False),
                PasswordResetToken.expires_at > datetime.now(UTC),
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def mark_token_used(self, token: PasswordResetToken) -> None:
        async with self._db_provider.session() as session:
            token = await session.merge(token)
            token.used = True
            await session.flush()
            await session.commit()

    async def has_team_memberships(self, user_id: int) -> bool:
        async with self._db_provider.session() as session:
            stmt = select(TeamMember).where(TeamMember.user_id == user_id).limit(1)
            result = await session.execute(stmt)
            return result.scalar_one_or_none() is not None

    async def has_career_paths(self, user_id: int) -> bool:
        async with self._db_provider.session() as session:
            stmt = select(UserCareerPath).where(UserCareerPath.user_id == user_id).limit(1)
            result = await session.execute(stmt)
            return result.scalar_one_or_none() is not None

    @staticmethod
    def to_domain(user: User) -> UserDomain:
        return UserDomain.model_validate(user.to_dict())

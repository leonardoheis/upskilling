from sqlalchemy import select
from sqlalchemy.orm import selectinload

from upskills.domain import RoleInfo
from upskills.domain import Team as TeamDomain
from upskills.domain import TeamMembership as TeamMembershipDomain
from upskills.domain import User as UserDomain
from upskills.repositories.base import BaseRepository
from upskills.repositories.user.models import User

from .models import Team, TeamMember


class TeamRepository(BaseRepository[Team]):
    async def get_by_id(self, id_value: int, id_column: str = "team_id") -> Team | None:
        async with self._db_provider.session() as session:
            stmt = (
                select(Team)
                .options(
                    selectinload(Team.manager),
                    selectinload(Team.members).selectinload(TeamMember.user),
                )
                .where(Team.team_id == id_value)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_all_with_details(self, *, skip: int = 0, limit: int = 100) -> list[Team]:
        async with self._db_provider.session() as session:
            stmt = (
                select(Team)
                .options(
                    selectinload(Team.manager),
                    selectinload(Team.members).selectinload(TeamMember.user),
                )
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_teams_by_manager(self, manager_user_id: int) -> list[Team]:
        async with self._db_provider.session() as session:
            stmt = (
                select(Team)
                .options(
                    selectinload(Team.manager),
                    selectinload(Team.members).selectinload(TeamMember.user),
                )
                .where(Team.manager_user_id == manager_user_id)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_teams_for_user(self, user_id: int) -> list[Team]:
        async with self._db_provider.session() as session:
            stmt = (
                select(Team).join(TeamMember).options(selectinload(Team.manager)).where(TeamMember.user_id == user_id)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def add_member(self, team_id: int, user_id: int) -> None:
        async with self._db_provider.session() as session:
            member = TeamMember(team_id=team_id, user_id=user_id)
            session.add(member)
            await session.flush()
            await session.commit()

    async def remove_member(self, team_id: int, user_id: int) -> None:
        async with self._db_provider.session() as session:
            stmt = select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
            result = await session.execute(stmt)
            member = result.scalar_one_or_none()
            if member:
                await session.delete(member)
                await session.flush()
                await session.commit()

    async def is_member(self, team_id: int, user_id: int) -> bool:
        async with self._db_provider.session() as session:
            stmt = select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none() is not None

    async def get_team_members(self, team_id: int) -> list[User]:
        async with self._db_provider.session() as session:
            stmt = select(User).join(TeamMember).where(TeamMember.team_id == team_id)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    @staticmethod
    def to_domain(team: Team) -> TeamDomain:
        manager_roles: list[RoleInfo] = []
        if team.manager and team.manager.roles:
            manager_roles = [
                RoleInfo(
                    role_id=user_role.role.role_id,
                    name=user_role.role.name,
                    description=user_role.role.description,
                    max_active_paths=user_role.role.max_active_paths,
                )
                for user_role in team.manager.roles
                if user_role.role
            ]

        manager = None
        if team.manager:
            manager = UserDomain(
                user_id=team.manager.user_id,
                full_name=team.manager.full_name,
                email=team.manager.email,
                bio=team.manager.bio,
                created_at=team.manager.created_at,
                roles=manager_roles,
            )

        members: list[TeamMembershipDomain] = []
        if team.members:
            members = [
                TeamMembershipDomain(
                    team_id=tm.team_id,
                    user_id=tm.user_id,
                    user=UserDomain(
                        user_id=tm.user.user_id,
                        full_name=tm.user.full_name,
                        email=tm.user.email,
                    )
                    if tm.user
                    else None,
                )
                for tm in team.members
            ]

        return TeamDomain(
            team_id=team.team_id,
            name=team.name,
            manager_user_id=team.manager_user_id,
            manager=manager,
            members=members,
        )

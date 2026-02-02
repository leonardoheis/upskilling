"""Team service."""

from typing import Any

from dependency_injector.wiring import Provide, inject

from upskills.models.db.team import Team
from upskills.models.domain.team import (
    TeamListResponse,
    TeamMemberResponse,
    TeamResponse,
    TeamWithMembersResponse,
)
from upskills.models.domain.user import UserResponse
from upskills.repositories.team import TeamRepository
from upskills.repositories.user import UserRepository


class TeamService:
    """Service for team operations."""

    @inject
    def __init__(
        self,
        team_repository: TeamRepository = Provide["team_repository"],
        user_repository: UserRepository = Provide["user_repository"],
    ) -> None:
        self._team_repository = team_repository
        self._user_repository = user_repository

    async def get_team(self, team_id: int) -> TeamWithMembersResponse | None:
        """Get a team by ID with members."""
        team = await self._team_repository.get_by_id(team_id)
        if not team:
            return None
        return self._team_to_response(team)

    async def get_all_teams(
        self, *, skip: int = 0, limit: int = 100
    ) -> tuple[list[TeamListResponse], int]:
        """Get all teams with summary info."""
        teams = await self._team_repository.get_all_with_details(skip=skip, limit=limit)
        total = await self._team_repository.count()

        return [
            TeamListResponse(
                team_id=t.team_id,
                name=t.name,
                member_count=len(t.members) if t.members else 0,
                manager_name=t.manager.full_name if t.manager else "Unknown",
            )
            for t in teams
        ], total

    async def get_teams_by_manager(self, manager_user_id: int) -> list[TeamWithMembersResponse]:
        """Get all teams managed by a user."""
        teams = await self._team_repository.get_teams_by_manager(manager_user_id)
        return [self._team_to_response(t) for t in teams]

    async def get_teams_for_user(self, user_id: int) -> list[TeamResponse]:
        """Get all teams a user is a member of."""
        teams = await self._team_repository.get_teams_for_user(user_id)
        return [
            TeamResponse(
                team_id=t.team_id,
                name=t.name,
                manager_user_id=t.manager_user_id,
            )
            for t in teams
        ]

    async def create_team(
        self,
        name: str,
        manager_user_id: int,
    ) -> TeamWithMembersResponse:
        """Create a new team."""
        # Verify manager exists
        manager = await self._user_repository.get_by_id(manager_user_id)
        if not manager:
            msg = "Manager user not found"
            raise ValueError(msg)

        team = await self._team_repository.create({
            "name": name,
            "manager_user_id": manager_user_id,
        })

        # Reload with relationships
        reloaded_team = await self._team_repository.get_by_id(team.team_id)
        if not reloaded_team:
            msg = "Failed to reload team after creation"
            raise RuntimeError(msg)
        return self._team_to_response(reloaded_team)

    async def update_team(
        self,
        team_id: int,
        name: str | None = None,
        manager_user_id: int | None = None,
    ) -> TeamWithMembersResponse | None:
        """Update a team."""
        team = await self._team_repository.get_by_id(team_id)
        if not team:
            return None

        if manager_user_id:
            manager = await self._user_repository.get_by_id(manager_user_id)
            if not manager:
                msg = "Manager user not found"
                raise ValueError(msg)

        update_data: dict[str, Any] = {}
        if name is not None:
            update_data["name"] = name
        if manager_user_id is not None:
            update_data["manager_user_id"] = manager_user_id

        if update_data:
            team = await self._team_repository.update(team, update_data)
            reloaded = await self._team_repository.get_by_id(team.team_id)
            if reloaded:
                team = reloaded

        return self._team_to_response(team)

    async def delete_team(self, team_id: int) -> bool:
        """Delete a team."""
        team = await self._team_repository.get_by_id(team_id)
        if not team:
            return False

        await self._team_repository.delete(team)
        return True

    async def add_member(self, team_id: int, user_id: int) -> bool:
        """Add a member to a team."""
        # Verify team exists
        team = await self._team_repository.get_by_id(team_id)
        if not team:
            msg = "Team not found"
            raise ValueError(msg)

        # Verify user exists
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            msg = "User not found"
            raise ValueError(msg)

        # Check if already a member
        if await self._team_repository.is_member(team_id, user_id):
            msg = "User is already a member of this team"
            raise ValueError(msg)

        await self._team_repository.add_member(team_id, user_id)
        return True

    async def remove_member(self, team_id: int, user_id: int) -> bool:
        """Remove a member from a team."""
        if not await self._team_repository.is_member(team_id, user_id):
            return False

        await self._team_repository.remove_member(team_id, user_id)
        return True

    async def get_team_members(self, team_id: int) -> list[TeamMemberResponse]:
        """Get all members of a team."""
        members = await self._team_repository.get_team_members(team_id)
        return [
            TeamMemberResponse(
                user_id=m.user_id,
                full_name=m.full_name,
                email=m.email,
            )
            for m in members
        ]

    @staticmethod
    def _team_to_response(team: Team) -> TeamWithMembersResponse:
        """Convert a Team model to TeamWithMembersResponse."""
        from upskills.models.domain.user import RoleResponse

        manager_roles: list[RoleResponse] = []
        if team.manager and team.manager.roles:
            manager_roles.extend(
                RoleResponse(
                    role_id=user_role.role.role_id,
                    name=user_role.role.name,
                    description=user_role.role.description,
                    max_active_paths=user_role.role.max_active_paths,
                )
                for user_role in team.manager.roles
                if user_role.role
            )

        manager_response = (
            UserResponse(
                user_id=team.manager.user_id,
                full_name=team.manager.full_name,
                email=team.manager.email,
                bio=team.manager.bio,
                created_at=team.manager.created_at,
                roles=manager_roles,
            )
            if team.manager
            else None
        )

        members: list[TeamMemberResponse] = []
        if team.members:
            members.extend(
                TeamMemberResponse(
                    user_id=tm.user.user_id,
                    full_name=tm.user.full_name,
                    email=tm.user.email,
                )
                for tm in team.members
                if tm.user
            )

        if not manager_response:
            msg = "Team manager not found"
            raise RuntimeError(msg)

        return TeamWithMembersResponse(
            team_id=team.team_id,
            name=team.name,
            manager_user_id=team.manager_user_id,
            manager=manager_response,
            members=members,
        )

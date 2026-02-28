from dataclasses import dataclass

from dependency_injector.wiring import Provide

from upskills.domain import Team, User
from upskills.repositories import TeamRepository, UserRepository


@dataclass
class TeamService:
    team_repository: TeamRepository = Provide["team_repository"]
    user_repository: UserRepository = Provide["user_repository"]

    async def get_team(self, team_id: int) -> Team | None:
        team = await self.team_repository.get_by_id(team_id)
        if not team:
            return None
        return self.team_repository.to_domain(team)

    async def get_all_teams(self, *, skip: int = 0, limit: int = 100) -> tuple[list[Team], int]:
        teams = await self.team_repository.get_all(skip=skip, limit=limit)
        total = await self.team_repository.count()
        return [self.team_repository.to_domain(t) for t in teams], total

    async def get_teams_by_manager(self, manager_user_id: int) -> list[Team]:
        teams = await self.team_repository.get_teams_by_manager(manager_user_id)
        return [self.team_repository.to_domain(t) for t in teams]

    async def get_teams_for_user(self, user_id: int) -> list[Team]:
        teams = await self.team_repository.get_teams_for_user(user_id)
        return [self.team_repository.to_domain(team) for team in teams]

    async def create_team(self, team_: Team) -> Team:
        manager = await self.user_repository.get_by_id(team_.manager_user_id)
        if not manager:
            msg = "Manager user not found"
            raise ValueError(msg)

        team = await self.team_repository.create(team_)
        return self.team_repository.to_domain(team)

    async def update_team(self, team_id: int, team_: Team) -> Team | None:
        team = await self.team_repository.get_by_id(team_id, id_column="team_id")
        if not team:
            return None

        if team_.manager_user_id:
            manager = await self.user_repository.get_by_id(team_.manager_user_id)
            if not manager:
                msg = "Manager user not found"
                raise ValueError(msg)

        updated_team = await self.team_repository.update(team, team_)
        return self.team_repository.to_domain(updated_team)

    async def delete_team(self, team_id: int) -> bool:
        team = await self.team_repository.get_by_id(team_id, id_column="team_id")
        if not team:
            return False
        await self.team_repository.delete(team)
        return True

    async def add_member(self, team_id: int, user_id: int) -> bool:
        team = await self.team_repository.get_by_id(team_id, id_column="team_id")
        if not team:
            msg = "Team not found"
            raise ValueError(msg)

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            msg = "User not found"
            raise ValueError(msg)

        if await self.team_repository.is_member(team_id, user_id):
            msg = "User is already a member of this team"
            raise ValueError(msg)

        await self.team_repository.add_member(team_id, user_id)
        return True

    async def remove_member(self, team_id: int, user_id: int) -> bool:
        team = await self.team_repository.get_by_id(team_id, id_column="team_id")
        if not team:
            return False
        await self.team_repository.remove_member(team.team_id, user_id)
        return True

    async def get_team_members(self, team_id: int) -> list[User]:
        members = await self.team_repository.get_team_members(team_id)
        return [self.user_repository.to_domain(member) for member in members]

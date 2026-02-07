from pydantic import Field

from .base import DomainModel
from .user import User


class Team(DomainModel):
    team_id: int
    name: str | None = None
    manager_user_id: int
    manager: User | None = None
    members: list["TeamMembership"] = Field(default_factory=list)


class TeamMembership(DomainModel):
    team_id: int | None = None
    user_id: int | None = None
    user: User | None = None

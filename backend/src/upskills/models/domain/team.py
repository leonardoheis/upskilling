"""Team-related Pydantic domain models."""

from pydantic import Field

from upskills.models.domain.base import DomainModel
from upskills.models.domain.user import UserResponse

# === Request Models ===


class TeamCreate(DomainModel):
    """Request model for creating a team."""

    name: str = Field(..., min_length=1, max_length=255)
    manager_user_id: int


class TeamUpdate(DomainModel):
    """Request model for updating a team."""

    name: str | None = Field(None, min_length=1, max_length=255)
    manager_user_id: int | None = None


class TeamMemberAdd(DomainModel):
    """Request model for adding a member to a team."""

    user_id: int


class TeamMemberBulkAdd(DomainModel):
    """Request model for adding multiple members to a team."""

    user_ids: list[int]


# === Response Models ===


class TeamMemberResponse(DomainModel):
    """Response model for a team member."""

    user_id: int
    full_name: str
    email: str


class TeamResponse(DomainModel):
    """Response model for a team."""

    team_id: int
    name: str
    manager_user_id: int


class TeamWithMembersResponse(TeamResponse):
    """Response model for a team with its members."""

    manager: UserResponse
    members: list[TeamMemberResponse] = Field(default_factory=list)


class TeamListResponse(DomainModel):
    """Response model for team list (for mentor view)."""

    team_id: int
    name: str
    member_count: int
    manager_name: str

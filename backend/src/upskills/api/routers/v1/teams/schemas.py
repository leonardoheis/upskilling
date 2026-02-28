from pydantic import Field

from upskills.api.schemas import BaseSchema, UserResponse


class TeamCreate(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    manager_user_id: int


class TeamUpdate(BaseSchema):
    name: str | None = Field(None, min_length=1, max_length=255)
    manager_user_id: int | None = None


class TeamMemberAdd(BaseSchema):
    user_id: int


class TeamMemberBulkAdd(BaseSchema):
    user_ids: list[int]


class TeamMemberResponse(BaseSchema):
    user_id: int
    full_name: str
    email: str


class TeamResponse(BaseSchema):
    team_id: int
    name: str
    manager_user_id: int


class TeamListResponse(BaseSchema):
    team_id: int
    name: str
    member_count: int
    manager_name: str


class TeamWithMembersResponse(BaseSchema):
    team_id: int
    name: str
    manager_user_id: int
    manager: UserResponse | None = None
    members: list[TeamMemberResponse] = Field(default_factory=list)


__all__ = [
    "TeamCreate",
    "TeamListResponse",
    "TeamMemberAdd",
    "TeamMemberBulkAdd",
    "TeamMemberResponse",
    "TeamResponse",
    "TeamUpdate",
    "TeamWithMembersResponse",
]

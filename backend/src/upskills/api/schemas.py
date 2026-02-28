from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
    )


class PaginatedResponse[T](BaseModel):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseModel):
    message: str
    detail: str | None = None


class RoleResponse(BaseSchema):
    role_id: int
    name: str
    description: str | None = None
    max_active_paths: int


class UserResponse(BaseSchema):
    user_id: int
    full_name: str
    email: str
    bio: str | None = None
    created_at: datetime
    roles: list[RoleResponse] = Field(default_factory=list)


class UserWithPermissionsResponse(UserResponse):
    permissions: list[str] = Field(default_factory=list)

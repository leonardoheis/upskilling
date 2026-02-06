from datetime import datetime

from pydantic import Field

from .base import DomainModel


class User(DomainModel):
    user_id: int
    full_name: str | None = None
    email: str | None = None
    password: str | None = None
    password_hash: str | None = None
    bio: str | None = None
    created_at: datetime | None = None
    roles: list["RoleInfo"] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)


class RoleInfo(DomainModel):
    role_id: int
    name: str
    description: str | None = None
    max_active_paths: int = 0

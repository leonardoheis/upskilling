from pydantic import EmailStr, Field

from upskills.api.schemas import BaseSchema


class UserUpdate(BaseSchema):
    full_name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    bio: str | None = None


class PasswordChange(BaseSchema):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)

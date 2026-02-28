from pydantic import Field

from upskills.api.schemas import BaseSchema


class CareerCreate(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    specialization: str | None = None


class CareerUpdate(BaseSchema):
    name: str | None = Field(None, min_length=1, max_length=255)
    specialization: str | None = None


class CareerResponse(BaseSchema):
    career_id: int
    name: str
    specialization: str | None = None


class PathTemplateBasicResponse(BaseSchema):
    path_template_id: int
    career_id: int
    name: str
    description: str | None = None
    duration_hours: int | None = None
    default_start_offset_days: int | None = None
    default_deadline_offset_days: int | None = None


class CareerWithPathsResponse(CareerResponse):
    path_templates: list[PathTemplateBasicResponse] = Field(default_factory=list)


__all__ = [
    "CareerCreate",
    "CareerResponse",
    "CareerUpdate",
    "CareerWithPathsResponse",
    "PathTemplateBasicResponse",
]

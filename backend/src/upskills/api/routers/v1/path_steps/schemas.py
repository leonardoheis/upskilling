from pydantic import Field

from upskills.api.schemas import BaseSchema


class PathStepCreate(BaseSchema):
    step_order: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    duration_hours: int | None = Field(None, gt=0)
    course_link: str | None = None


class PathStepUpdate(BaseSchema):
    step_order: int | None = Field(None, ge=1)
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    duration_hours: int | None = Field(None, gt=0)
    course_link: str | None = None


class StepDependencyCreate(BaseSchema):
    depends_on_step_id: int


class PathStepDependencyResponse(BaseSchema):
    depends_on_step_id: int
    depends_on_step_name: str | None = None


class PathStepResponse(BaseSchema):
    step_id: int
    path_template_id: int
    step_order: int
    name: str
    description: str | None = None
    duration_hours: int | None = None
    course_link: str | None = None
    dependencies: list[PathStepDependencyResponse] = Field(default_factory=list)


__all__ = [
    "PathStepCreate",
    "PathStepDependencyResponse",
    "PathStepResponse",
    "PathStepUpdate",
    "StepDependencyCreate",
]

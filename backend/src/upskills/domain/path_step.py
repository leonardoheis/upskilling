from pydantic import Field

from .base import DomainModel


class PathStepDependency(DomainModel):
    depends_on_step_id: int
    depends_on_step_name: str | None = None


class PathStep(DomainModel):
    step_id: int
    path_template_id: int
    step_order: int | None = None
    name: str | None = None
    description: str | None = None
    duration_hours: int | None = None
    course_link: str | None = None
    dependencies: list[PathStepDependency] = Field(default_factory=list)

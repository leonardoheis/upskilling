"""Career and path template Pydantic domain models."""

from pydantic import Field

from .base import DomainModel

# === Request Models ===


class CareerCreate(DomainModel):
    """Request model for creating a career."""

    name: str = Field(..., min_length=1, max_length=255)
    specialization: str | None = None


class CareerUpdate(DomainModel):
    """Request model for updating a career."""

    name: str | None = Field(None, min_length=1, max_length=255)
    specialization: str | None = None


class PathTemplateCreate(DomainModel):
    """Request model for creating a path template."""

    career_id: int
    name: str = Field(..., min_length=1, max_length=255)
    description: str
    duration_hours: int = Field(..., gt=0)
    default_start_offset_days: int | None = None
    default_deadline_offset_days: int | None = None


class PathTemplateUpdate(DomainModel):
    """Request model for updating a path template."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    duration_hours: int | None = Field(None, gt=0)
    default_start_offset_days: int | None = None
    default_deadline_offset_days: int | None = None


class PathStepCreate(DomainModel):
    """Request model for creating a path step."""

    path_template_id: int
    step_order: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    duration_hours: int | None = Field(None, gt=0)
    course_link: str | None = None


class PathStepUpdate(DomainModel):
    """Request model for updating a path step."""

    step_order: int | None = Field(None, ge=1)
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    duration_hours: int | None = Field(None, gt=0)
    course_link: str | None = None


class StepDependencyCreate(DomainModel):
    """Request model for creating a step dependency."""

    step_id: int
    depends_on_step_id: int


# === Response Models ===


class CareerResponse(DomainModel):
    """Response model for a career."""

    career_id: int
    name: str
    specialization: str | None


class PathStepDependencyResponse(DomainModel):
    """Response model for a step dependency."""

    depends_on_step_id: int
    depends_on_step_name: str


class PathStepResponse(DomainModel):
    """Response model for a path step."""

    step_id: int
    path_template_id: int
    step_order: int
    name: str
    description: str | None
    duration_hours: int | None
    course_link: str | None
    dependencies: list[PathStepDependencyResponse] = Field(default_factory=list)


class PathTemplateResponse(DomainModel):
    """Response model for a path template."""

    path_template_id: int
    career_id: int
    name: str
    description: str
    duration_hours: int
    default_start_offset_days: int | None
    default_deadline_offset_days: int | None


class PathTemplateWithStepsResponse(PathTemplateResponse):
    """Response model for a path template with its steps."""

    steps: list[PathStepResponse] = Field(default_factory=list)


class CareerWithPathsResponse(CareerResponse):
    """Response model for a career with its path templates."""

    path_templates: list[PathTemplateResponse] = Field(default_factory=list)


# Input models for service layer
class PathTemplateCreateInput(DomainModel):
    """Input model for creating a path template."""

    career_id: int
    name: str
    description: str
    duration_hours: int
    default_start_offset_days: int | None = None
    default_deadline_offset_days: int | None = None


class PathTemplateUpdateInput(DomainModel):
    """Input model for updating a path template."""

    name: str | None = None
    description: str | None = None
    duration_hours: int | None = None
    default_start_offset_days: int | None = None
    default_deadline_offset_days: int | None = None


class PathStepCreateInput(DomainModel):
    """Input model for creating a path step."""

    path_template_id: int
    step_order: int
    name: str
    description: str | None = None
    duration_hours: int | None = None
    course_link: str | None = None


class PathStepUpdateInput(DomainModel):
    """Input model for updating a path step."""

    step_order: int | None = None
    name: str | None = None
    description: str | None = None
    duration_hours: int | None = None
    course_link: str | None = None

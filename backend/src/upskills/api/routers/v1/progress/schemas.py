from datetime import date

from pydantic import Field

from upskills.api.routers.v1.path_steps.schemas import PathStepResponse
from upskills.api.routers.v1.path_templates.schemas import PathTemplateResponse
from upskills.api.schemas import BaseSchema
from upskills.domain import ProgressStatus, ValidationStatus


class DashboardStats(BaseSchema):
    current_career: str | None
    current_path: str | None
    current_path_progress: int
    paths_remaining: int
    overall_progress: int
    skills_obtained: int


class MenteeProgressSummary(BaseSchema):
    user_id: int
    full_name: str
    email: str
    career_name: str
    start_date: date
    end_date: date
    overall_progress_percent: int
    paths_completed: int
    paths_total: int
    pending_validation: int


class UserCareerPathCreate(BaseSchema):
    user_id: int
    career_id: int
    start_date: date
    end_date: date


class UserCareerPathUpdate(BaseSchema):
    start_date: date | None = None
    end_date: date | None = None


class UserCareerPathResponse(BaseSchema):
    user_career_path_id: int
    user_id: int
    career_id: int
    start_date: date
    end_date: date
    overall_progress_percent: int


class UserPathAssignmentResponse(BaseSchema):
    user_path_assignment_id: int
    user_career_path_id: int
    path_template_id: int
    start_date: date
    deadline: date
    status: str
    progress_percent: int
    mentor_validation_status: str


class UserCareerPathDetailResponse(UserCareerPathResponse):
    career_name: str
    career_specialization: str | None
    path_assignments: list[UserPathAssignmentResponse] = Field(default_factory=list)


class UserPathAssignmentCreate(BaseSchema):
    user_career_path_id: int
    path_template_id: int
    start_date: date
    deadline: date


class UserPathAssignmentUpdate(BaseSchema):
    start_date: date | None = None
    deadline: date | None = None
    status: ProgressStatus | None = None
    mentor_validation_status: ValidationStatus | None = None


class UserStepProgressResponse(BaseSchema):
    user_step_progress_id: int
    user_path_assignment_id: int
    step_id: int
    status: str
    progress_percent: int
    planned_start_date: date | None
    planned_end_date: date | None
    actual_start_date: date | None
    actual_end_date: date | None
    step: PathStepResponse | None = None


class UserPathAssignmentDetailResponse(UserPathAssignmentResponse):
    path_template: PathTemplateResponse | None = None
    step_progress: list[UserStepProgressResponse] = Field(default_factory=list)


class UserStepProgressUpdate(BaseSchema):
    status: ProgressStatus | None = None
    progress_percent: int | None = Field(None, ge=0, le=100)
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    actual_start_date: date | None = None
    actual_end_date: date | None = None


__all__ = [
    "DashboardStats",
    "MenteeProgressSummary",
    "UserCareerPathCreate",
    "UserCareerPathDetailResponse",
    "UserCareerPathResponse",
    "UserCareerPathUpdate",
    "UserPathAssignmentCreate",
    "UserPathAssignmentDetailResponse",
    "UserPathAssignmentResponse",
    "UserPathAssignmentUpdate",
    "UserStepProgressResponse",
    "UserStepProgressUpdate",
]

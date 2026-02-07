from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import Field

from .base import DomainModel
from .path_step import PathStep
from .path_template import PathTemplate

if TYPE_CHECKING:
    from .career import Career


class ProgressStatus(StrEnum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class ValidationStatus(StrEnum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class DashboardStats(DomainModel):
    current_career: str | None = None
    current_path: str | None = None
    current_path_progress: int = 0
    paths_remaining: int = 0
    overall_progress: int = 0
    skills_obtained: int = 0


class MenteeProgressSummary(DomainModel):
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


class UserStepProgress(DomainModel):
    user_step_progress_id: int
    user_path_assignment_id: int
    step_id: int
    status: str | None = None
    progress_percent: int = 0
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    actual_start_date: date | None = None
    actual_end_date: date | None = None
    updated_at: datetime | None = None
    step: PathStep | None = None


class UserPathAssignment(DomainModel):
    user_path_assignment_id: int
    user_career_path_id: int
    path_template_id: int
    start_date: date | None = None
    deadline: date | None = None
    status: str | None = None
    progress_percent: int = 0
    mentor_validation_status: str | None = None
    path_template: PathTemplate | None = None
    step_progress: list[UserStepProgress] = Field(default_factory=list)


class UserCareerPath(DomainModel):
    user_career_path_id: int
    user_id: int
    career_id: int
    start_date: date | None = None
    end_date: date | None = None
    overall_progress_percent: int = 0
    career_name: str | None = None
    career_specialization: str | None = None
    career: "Career | None" = None
    path_assignments: list[UserPathAssignment] = Field(default_factory=list)

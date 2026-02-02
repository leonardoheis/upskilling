"""Progress tracking Pydantic domain models."""

from datetime import date, datetime
from enum import StrEnum

from pydantic import Field

from upskills.models.domain.base import DomainModel
from upskills.models.domain.career import PathStepResponse, PathTemplateResponse


class ProgressStatus(StrEnum):
    """Status values for progress tracking."""

    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class ValidationStatus(StrEnum):
    """Mentor validation status values."""

    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class LogEntryType(StrEnum):
    """Log entry type values."""

    MEETING = "Meeting/Conversation"
    PATH_APPROVED = "Path Approved"
    PATH_REJECTED = "Path Rejected"
    FINAL_PROJECT = "Final Project"
    GENERAL = "General"


# === Request Models ===


class UserCareerPathCreate(DomainModel):
    """Request model for assigning a career path to a user."""

    user_id: int
    career_id: int
    start_date: date
    end_date: date


class UserCareerPathUpdate(DomainModel):
    """Request model for updating a user's career path."""

    start_date: date | None = None
    end_date: date | None = None


class UserPathAssignmentCreate(DomainModel):
    """Request model for assigning a path to a user's career."""

    user_career_path_id: int
    path_template_id: int
    start_date: date
    deadline: date


class UserPathAssignmentUpdate(DomainModel):
    """Request model for updating a path assignment."""

    start_date: date | None = None
    deadline: date | None = None
    status: ProgressStatus | None = None
    mentor_validation_status: ValidationStatus | None = None


class UserStepProgressUpdate(DomainModel):
    """Request model for updating step progress."""

    status: ProgressStatus | None = None
    progress_percent: int | None = Field(None, ge=0, le=100)
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    actual_start_date: date | None = None
    actual_end_date: date | None = None


class LogEntryCreate(DomainModel):
    """Request model for creating a log entry."""

    user_id: int
    user_career_path_id: int
    entry_type: LogEntryType
    entry_date: date
    notes: str = Field(..., min_length=1)
    related_user_path_assignment_id: int | None = None


class LogEntryUpdate(DomainModel):
    """Request model for updating a log entry."""

    entry_type: LogEntryType | None = None
    entry_date: date | None = None
    notes: str | None = Field(None, min_length=1)


# === Response Models ===


class UserStepProgressResponse(DomainModel):
    """Response model for step progress."""

    user_step_progress_id: int
    user_path_assignment_id: int
    step_id: int
    status: str
    progress_percent: int
    planned_start_date: date | None
    planned_end_date: date | None
    actual_start_date: date | None
    actual_end_date: date | None
    updated_at: datetime
    step: PathStepResponse | None = None


class UserPathAssignmentResponse(DomainModel):
    """Response model for a path assignment."""

    user_path_assignment_id: int
    user_career_path_id: int
    path_template_id: int
    start_date: date
    deadline: date
    status: str
    progress_percent: int
    mentor_validation_status: str


class UserPathAssignmentDetailResponse(UserPathAssignmentResponse):
    """Detailed response model for a path assignment with related data."""

    path_template: PathTemplateResponse | None = None
    step_progress: list[UserStepProgressResponse] = Field(default_factory=list)


class UserCareerPathResponse(DomainModel):
    """Response model for a user's career path."""

    user_career_path_id: int
    user_id: int
    career_id: int
    start_date: date
    end_date: date
    overall_progress_percent: int


class UserCareerPathDetailResponse(UserCareerPathResponse):
    """Detailed response model for a user's career path."""

    career_name: str
    career_specialization: str | None
    path_assignments: list[UserPathAssignmentResponse] = Field(default_factory=list)


class LogEntryResponse(DomainModel):
    """Response model for a log entry."""

    log_entry_id: int
    user_id: int
    user_career_path_id: int
    entry_type: str
    entry_date: date
    notes: str
    related_user_path_assignment_id: int | None


class LogEntryDetailResponse(LogEntryResponse):
    """Detailed log entry response with related info."""

    user_name: str
    path_name: str | None = None


# === Dashboard Models ===


class MenteeProgressSummary(DomainModel):
    """Summary of a mentee's progress (for team management view)."""

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


class DashboardStats(DomainModel):
    """Dashboard statistics for a user."""

    current_career: str | None
    current_path: str | None
    current_path_progress: int
    paths_remaining: int
    overall_progress: int
    skills_obtained: int


# === Input Models ===


class LogEntryCreateInput(DomainModel):
    """Input model for creating a log entry."""

    user_id: int
    user_career_path_id: int
    entry_type: str
    entry_date: date
    notes: str
    related_user_path_assignment_id: int | None = None


class StepProgressUpdateInput(DomainModel):
    """Input model for updating step progress."""

    status: str | None = None
    progress_percent: int | None = None
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    actual_start_date: date | None = None
    actual_end_date: date | None = None

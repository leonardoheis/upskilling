"""Progress tracking SQLAlchemy models."""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from upskills.models.db.base import Base

if TYPE_CHECKING:
    from upskills.models.db.career import Career, PathTemplate, PathTemplateStep
    from upskills.models.db.user import User


class UserCareerPath(Base):
    """User's assigned career track."""

    __tablename__ = "user_career_paths"

    user_career_path_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    career_id: Mapped[int] = mapped_column(ForeignKey("careers.career_id"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    overall_progress_percent: Mapped[int] = mapped_column(default=0)

    __table_args__ = (
        CheckConstraint("overall_progress_percent >= 0 AND overall_progress_percent <= 100"),
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="career_paths")
    career: Mapped["Career"] = relationship(back_populates="user_career_paths")
    path_assignments: Mapped[list["UserPathAssignment"]] = relationship(
        back_populates="user_career_path", lazy="selectin"
    )
    log_entries: Mapped[list["LogEntry"]] = relationship(
        back_populates="user_career_path", lazy="selectin"
    )


class UserPathAssignment(Base):
    """Concrete assignment of a path template to a user's career journey."""

    __tablename__ = "user_path_assignments"

    user_path_assignment_id: Mapped[int] = mapped_column(primary_key=True)
    user_career_path_id: Mapped[int] = mapped_column(
        ForeignKey("user_career_paths.user_career_path_id")
    )
    path_template_id: Mapped[int] = mapped_column(ForeignKey("path_templates.path_template_id"))
    start_date: Mapped[date] = mapped_column(Date)
    deadline: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="Pending")
    progress_percent: Mapped[int] = mapped_column(default=0)
    mentor_validation_status: Mapped[str] = mapped_column(String(20), default="Pending")

    __table_args__ = (
        CheckConstraint("status IN ('Pending', 'In Progress', 'Completed')"),
        CheckConstraint("progress_percent >= 0 AND progress_percent <= 100"),
        CheckConstraint("mentor_validation_status IN ('Pending', 'Approved', 'Rejected')"),
    )

    # Relationships
    user_career_path: Mapped["UserCareerPath"] = relationship(back_populates="path_assignments")
    path_template: Mapped["PathTemplate"] = relationship(back_populates="assignments")
    step_progress: Mapped[list["UserStepProgress"]] = relationship(
        back_populates="path_assignment", lazy="selectin"
    )
    log_entries: Mapped[list["LogEntry"]] = relationship(
        back_populates="related_path_assignment", lazy="selectin"
    )


class UserStepProgress(Base):
    """Progress on individual steps within an assigned path."""

    __tablename__ = "user_step_progress"

    user_step_progress_id: Mapped[int] = mapped_column(primary_key=True)
    user_path_assignment_id: Mapped[int] = mapped_column(
        ForeignKey("user_path_assignments.user_path_assignment_id")
    )
    step_id: Mapped[int] = mapped_column(ForeignKey("path_template_steps.step_id"))
    status: Mapped[str] = mapped_column(String(20), default="Pending")
    progress_percent: Mapped[int] = mapped_column(default=0)
    planned_start_date: Mapped[date | None] = mapped_column(Date)
    planned_end_date: Mapped[date | None] = mapped_column(Date)
    actual_start_date: Mapped[date | None] = mapped_column(Date)
    actual_end_date: Mapped[date | None] = mapped_column(Date)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("status IN ('Pending', 'In Progress', 'Completed')"),
        CheckConstraint("progress_percent >= 0 AND progress_percent <= 100"),
    )

    # Relationships
    path_assignment: Mapped["UserPathAssignment"] = relationship(back_populates="step_progress")
    step: Mapped["PathTemplateStep"] = relationship()


class LogEntry(Base):
    """Logbook entry for mentor-mentee interactions."""

    __tablename__ = "log_entries"

    log_entry_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    user_career_path_id: Mapped[int] = mapped_column(
        ForeignKey("user_career_paths.user_career_path_id")
    )
    entry_type: Mapped[str] = mapped_column(String(50))
    entry_date: Mapped[date] = mapped_column(Date)
    notes: Mapped[str] = mapped_column(Text)
    related_user_path_assignment_id: Mapped[int | None] = mapped_column(
        ForeignKey("user_path_assignments.user_path_assignment_id")
    )

    __table_args__ = (
        CheckConstraint(
            "entry_type IN ('Meeting/Conversation', 'Path Approved', "
            "'Path Rejected', 'Final Project', 'General')"
        ),
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="log_entries")
    user_career_path: Mapped["UserCareerPath"] = relationship(back_populates="log_entries")
    related_path_assignment: Mapped["UserPathAssignment | None"] = relationship(
        back_populates="log_entries"
    )

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from upskills.repositories.base import Base

if TYPE_CHECKING:
    from upskills.repositories.log_entry.models import LogEntry
    from upskills.repositories.path_template.models import PathTemplate
    from upskills.repositories.user_career_path.models import UserCareerPath
    from upskills.repositories.user_step_progress.models import UserStepProgress


class UserPathAssignment(Base):  # pylint: disable=too-few-public-methods R0903
    __tablename__ = "user_path_assignments"

    user_path_assignment_id: Mapped[int] = mapped_column(primary_key=True)
    user_career_path_id: Mapped[int] = mapped_column(ForeignKey("user_career_paths.user_career_path_id"))
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

    user_career_path: Mapped["UserCareerPath"] = relationship(back_populates="path_assignments")
    path_template: Mapped["PathTemplate"] = relationship(back_populates="assignments")
    step_progress: Mapped[list["UserStepProgress"]] = relationship(back_populates="path_assignment", lazy="selectin")
    log_entries: Mapped[list["LogEntry"]] = relationship(back_populates="related_path_assignment", lazy="selectin")

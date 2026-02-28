from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from upskills.repositories.base import Base

if TYPE_CHECKING:
    from upskills.repositories.path_template.models import PathTemplateStep
    from upskills.repositories.user_path_assignment.models import UserPathAssignment


class UserStepProgress(Base):  # pylint: disable=too-few-public-methods R0903
    __tablename__ = "user_step_progress"

    user_step_progress_id: Mapped[int] = mapped_column(primary_key=True)
    user_path_assignment_id: Mapped[int] = mapped_column(ForeignKey("user_path_assignments.user_path_assignment_id"))
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

    path_assignment: Mapped["UserPathAssignment"] = relationship(back_populates="step_progress")
    step: Mapped["PathTemplateStep"] = relationship()

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from upskills.repositories.base import Base

if TYPE_CHECKING:
    from upskills.repositories.user.models import User
    from upskills.repositories.user_career_path.models import UserCareerPath
    from upskills.repositories.user_path_assignment.models import UserPathAssignment


class LogEntry(Base):  # pylint: disable=too-few-public-methods R0903
    __tablename__ = "log_entries"

    log_entry_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    user_career_path_id: Mapped[int] = mapped_column(ForeignKey("user_career_paths.user_career_path_id"))
    entry_type: Mapped[str] = mapped_column(String(50))
    entry_date: Mapped[date] = mapped_column(Date)
    notes: Mapped[str] = mapped_column(Text)
    related_user_path_assignment_id: Mapped[int | None] = mapped_column(
        ForeignKey("user_path_assignments.user_path_assignment_id")
    )

    __table_args__ = (
        CheckConstraint(
            "entry_type IN ('Meeting/Conversation', 'Path Approved', 'Path Rejected', 'Final Project', 'General')"
        ),
    )

    user: Mapped["User"] = relationship(back_populates="log_entries")
    user_career_path: Mapped["UserCareerPath"] = relationship(back_populates="log_entries")
    related_path_assignment: Mapped["UserPathAssignment | None"] = relationship(back_populates="log_entries")

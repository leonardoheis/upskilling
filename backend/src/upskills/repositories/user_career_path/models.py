from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from upskills.repositories.base import Base

if TYPE_CHECKING:
    from upskills.repositories.career.models import Career
    from upskills.repositories.log_entry.models import LogEntry
    from upskills.repositories.user.models import User
    from upskills.repositories.user_path_assignment.models import UserPathAssignment


class UserCareerPath(Base):  # pylint: disable=too-few-public-methods R0903
    __tablename__ = "user_career_paths"

    user_career_path_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    career_id: Mapped[int] = mapped_column(ForeignKey("careers.career_id"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    overall_progress_percent: Mapped[int] = mapped_column(default=0)

    __table_args__ = (CheckConstraint("overall_progress_percent >= 0 AND overall_progress_percent <= 100"),)

    user: Mapped["User"] = relationship(back_populates="career_paths")
    career: Mapped["Career"] = relationship(back_populates="user_career_paths")
    path_assignments: Mapped[list["UserPathAssignment"]] = relationship(
        back_populates="user_career_path", lazy="selectin"
    )
    log_entries: Mapped[list["LogEntry"]] = relationship(back_populates="user_career_path", lazy="selectin")

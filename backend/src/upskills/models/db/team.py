"""Team-related SQLAlchemy models."""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from upskills.models.db.base import Base

if TYPE_CHECKING:
    from upskills.models.db.user import User


class Team(Base):
    """Team model - groups of users managed by a manager."""

    __tablename__ = "teams"

    team_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    manager_user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))

    # Relationships
    manager: Mapped["User"] = relationship(back_populates="managed_teams")
    members: Mapped[list["TeamMember"]] = relationship(back_populates="team", lazy="selectin")


class TeamMember(Base):
    """Team-User association table."""

    __tablename__ = "team_members"

    team_id: Mapped[int] = mapped_column(ForeignKey("teams.team_id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)

    # Relationships
    team: Mapped["Team"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="team_memberships")

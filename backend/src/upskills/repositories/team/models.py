from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from upskills.repositories.base import Base

if TYPE_CHECKING:
    from upskills.repositories.user.models import User


class Team(Base):  # pylint: disable=too-few-public-methods R0903
    __tablename__ = "teams"

    team_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    manager_user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))

    manager: Mapped["User"] = relationship(back_populates="managed_teams")
    members: Mapped[list["TeamMember"]] = relationship(back_populates="team", lazy="selectin")


class TeamMember(Base):  # pylint: disable=too-few-public-methods R0903
    __tablename__ = "team_members"

    team_id: Mapped[int] = mapped_column(ForeignKey("teams.team_id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)

    team: Mapped["Team"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="team_memberships")

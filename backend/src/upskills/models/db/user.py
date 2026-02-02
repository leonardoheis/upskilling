"""User-related SQLAlchemy models."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from upskills.models.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from upskills.models.db.progress import LogEntry, UserCareerPath
    from upskills.models.db.team import Team, TeamMember


class User(Base, TimestampMixin):
    """User model - people in the system."""

    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    bio: Mapped[str | None] = mapped_column(Text)

    # Relationships
    roles: Mapped[list["UserRole"]] = relationship(back_populates="user", lazy="selectin")
    managed_teams: Mapped[list["Team"]] = relationship(back_populates="manager", lazy="selectin")
    team_memberships: Mapped[list["TeamMember"]] = relationship(
        back_populates="user", lazy="selectin"
    )
    career_paths: Mapped[list["UserCareerPath"]] = relationship(
        back_populates="user", lazy="selectin"
    )
    log_entries: Mapped[list["LogEntry"]] = relationship(back_populates="user", lazy="selectin")


class Role(Base):
    """Role model - system roles (admin, mentor, mentee, path_creator)."""

    __tablename__ = "roles"

    role_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    max_active_paths: Mapped[int | None] = mapped_column()

    # Relationships
    users: Mapped[list["UserRole"]] = relationship(back_populates="role", lazy="selectin")
    actions: Mapped[list["RoleAction"]] = relationship(back_populates="role", lazy="selectin")


class Action(Base):
    """Action model - atomic permissions."""

    __tablename__ = "actions"

    action_id: Mapped[int] = mapped_column(primary_key=True)
    action_key: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(Text)

    # Relationships
    roles: Mapped[list["RoleAction"]] = relationship(back_populates="action", lazy="selectin")


class UserRole(Base):
    """User-Role association table."""

    __tablename__ = "user_roles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.role_id"), primary_key=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="roles")
    role: Mapped["Role"] = relationship(back_populates="users")


class RoleAction(Base):
    """Role-Action association table."""

    __tablename__ = "role_actions"

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.role_id"), primary_key=True)
    action_id: Mapped[int] = mapped_column(ForeignKey("actions.action_id"), primary_key=True)

    # Relationships
    role: Mapped["Role"] = relationship(back_populates="actions")
    action: Mapped["Action"] = relationship(back_populates="roles")


class PasswordResetToken(Base):
    """Password reset token model."""

    __tablename__ = "password_reset_tokens"

    token_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    token: Mapped[str] = mapped_column(String(255), unique=True)
    expires_at: Mapped[datetime] = mapped_column()
    used: Mapped[bool] = mapped_column(default=False)

    # Relationships
    user: Mapped["User"] = relationship()

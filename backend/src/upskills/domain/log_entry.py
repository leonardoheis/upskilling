from datetime import date
from enum import StrEnum
from typing import TYPE_CHECKING

from .base import DomainModel

if TYPE_CHECKING:
    from .progress import UserPathAssignment
    from .user import User


class LogEntryType(StrEnum):
    MEETING = "Meeting/Conversation"
    PATH_APPROVED = "Path Approved"
    PATH_REJECTED = "Path Rejected"
    FINAL_PROJECT = "Final Project"
    GENERAL = "General"


class LogEntry(DomainModel):
    log_entry_id: int
    user_id: int
    user_career_path_id: int
    entry_type: str | None = None
    entry_date: date | None = None
    notes: str | None = None
    related_user_path_assignment_id: int | None = None
    user_name: str | None = None
    path_name: str | None = None
    user: "User | None" = None
    related_path_assignment: "UserPathAssignment | None" = None

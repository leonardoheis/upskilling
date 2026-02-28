from sqlalchemy import select
from sqlalchemy.orm import selectinload

from upskills.domain import LogEntry as LogEntryDomain
from upskills.repositories.base import BaseRepository
from upskills.repositories.user_path_assignment.models import UserPathAssignment

from .models import LogEntry


class LogEntryRepository(BaseRepository[LogEntry]):
    async def get_by_id(self, id_value: int, id_column: str = "log_entry_id") -> LogEntry | None:
        async with self._db_provider.session() as session:
            stmt = (
                select(LogEntry)
                .options(
                    selectinload(LogEntry.user),
                    selectinload(LogEntry.related_path_assignment).selectinload(UserPathAssignment.path_template),
                )
                .where(LogEntry.log_entry_id == id_value)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_career_path(self, user_career_path_id: int, entry_type: str | None = None) -> list[LogEntryDomain]:
        async with self._db_provider.session() as session:
            stmt = (
                select(LogEntry)
                .options(
                    selectinload(LogEntry.user),
                    selectinload(LogEntry.related_path_assignment).selectinload(UserPathAssignment.path_template),
                )
                .where(LogEntry.user_career_path_id == user_career_path_id)
            )

            if entry_type:
                stmt = stmt.where(LogEntry.entry_type == entry_type)

            stmt = stmt.order_by(LogEntry.entry_date.desc())
            result = await session.execute(stmt)
            return [self.to_domain(e, include_details=True) for e in result.scalars().all()]

    async def get_by_user(self, user_id: int) -> list[LogEntryDomain]:
        async with self._db_provider.session() as session:
            stmt = (
                select(LogEntry)
                .options(selectinload(LogEntry.related_path_assignment))
                .where(LogEntry.user_id == user_id)
                .order_by(LogEntry.entry_date.desc())
            )
            result = await session.execute(stmt)
            return [self.to_domain(e) for e in result.scalars().all()]

    @staticmethod
    def to_domain(entry: LogEntry, *, include_details: bool = False) -> LogEntryDomain:
        path_name = None
        user_name = None

        if include_details:
            if entry.related_path_assignment and entry.related_path_assignment.path_template:
                path_name = entry.related_path_assignment.path_template.name
            user_name = entry.user.full_name if entry.user else "Unknown"

        return LogEntryDomain(
            log_entry_id=entry.log_entry_id,
            user_id=entry.user_id,
            user_career_path_id=entry.user_career_path_id,
            entry_type=entry.entry_type,
            entry_date=entry.entry_date,
            notes=entry.notes,
            related_user_path_assignment_id=entry.related_user_path_assignment_id,
            user_name=user_name,
            path_name=path_name,
        )

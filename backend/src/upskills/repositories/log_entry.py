"""Log entry repository."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from upskills.models.db.progress import LogEntry, UserPathAssignment
from upskills.repositories.base import BaseRepository


class LogEntryRepository(BaseRepository[LogEntry]):
    """Repository for LogEntry operations."""

    async def get_by_id(
        self, log_entry_id: int, id_column: str = "log_entry_id"
    ) -> LogEntry | None:
        """Get log entry by ID."""
        async with self._db_provider.session() as session:
            stmt = (
                select(LogEntry)
                .options(
                    selectinload(LogEntry.user),
                    selectinload(LogEntry.related_path_assignment),
                )
                .where(LogEntry.log_entry_id == log_entry_id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_career_path(
        self, user_career_path_id: int, entry_type: str | None = None
    ) -> list[LogEntry]:
        """Get all log entries for a career path."""
        async with self._db_provider.session() as session:
            stmt = (
                select(LogEntry)
                .options(
                    selectinload(LogEntry.user),
                    selectinload(LogEntry.related_path_assignment).selectinload(
                        UserPathAssignment.path_template
                    ),
                )
                .where(LogEntry.user_career_path_id == user_career_path_id)
            )

            if entry_type:
                stmt = stmt.where(LogEntry.entry_type == entry_type)

            stmt = stmt.order_by(LogEntry.entry_date.desc())
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_by_user(self, user_id: int) -> list[LogEntry]:
        """Get all log entries about a user."""
        async with self._db_provider.session() as session:
            stmt = (
                select(LogEntry)
                .options(selectinload(LogEntry.related_path_assignment))
                .where(LogEntry.user_id == user_id)
                .order_by(LogEntry.entry_date.desc())
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

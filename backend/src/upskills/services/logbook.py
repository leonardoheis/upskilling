from dataclasses import dataclass

from dependency_injector.wiring import Provide

from upskills.domain import LogEntry
from upskills.repositories import LogEntryRepository, UserCareerPathRepository


@dataclass
class LogbookService:
    log_repository: LogEntryRepository = Provide["log_entry_repository"]
    career_path_repository: UserCareerPathRepository = Provide["user_career_path_repository"]

    async def get_for_career_path(
        self,
        user_career_path_id: int,
        entry_type: str | None = None,
    ) -> list[LogEntry]:
        return await self.log_repository.get_by_career_path(user_career_path_id, entry_type)

    async def get(self, log_entry_id: int) -> LogEntry | None:
        log_entry = await self.log_repository.get_by_id(log_entry_id)
        if not log_entry:
            return None
        return self.log_repository.to_domain(log_entry, include_details=True)

    async def create(self, log_entry_: LogEntry) -> LogEntry:
        career_path = await self.career_path_repository.get_by_id(
            log_entry_.user_career_path_id, id_column="user_career_path_id"
        )
        if not career_path:
            msg = "Career path not found"
            raise ValueError(msg)

        log_entry = await self.log_repository.create(log_entry_)
        return self.log_repository.to_domain(log_entry)

    async def update(self, log_entry_id: int, log_entry_: LogEntry) -> LogEntry | None:
        log_entry = await self.log_repository.get_by_id(log_entry_id, id_column="log_entry_id")
        if not log_entry:
            return None
        updated_log_entry = await self.log_repository.update(log_entry, log_entry_)
        return self.log_repository.to_domain(updated_log_entry)

    async def delete(self, log_entry_id: int) -> bool:
        log_entry = await self.log_repository.get_by_id(log_entry_id, id_column="log_entry_id")
        if not log_entry:
            return False
        await self.log_repository.delete(log_entry)
        return True

from dataclasses import dataclass

from dependency_injector.wiring import Provide

from upskills.domain import Career
from upskills.repositories import CareerRepository


@dataclass
class CareerService:
    career_repository: CareerRepository = Provide["career_repository"]

    async def get(self, career_id: int) -> Career | None:
        career_db = await self.career_repository.get_by_id(career_id)
        if not career_db:
            return None
        return self.career_repository.to_domain(career_db, include_paths=True)

    async def get_all(self, *, skip: int = 0, limit: int = 100) -> tuple[list[Career], int]:
        careers_db = await self.career_repository.get_all_with_paths(skip=skip, limit=limit)
        total = await self.career_repository.count()
        return [self.career_repository.to_domain(c) for c in careers_db], total

    async def create(self, career: Career) -> Career:
        career_db = await self.career_repository.create(career.model_dump(include={"name", "specialization"}))
        return self.career_repository.to_domain(career_db)

    async def update(self, career_id: int, career: Career) -> Career | None:
        career_db = await self.career_repository.get_by_id(career_id)
        if not career_db:
            return None

        update_data = career.model_dump(include={"name", "specialization"}, exclude_none=True)

        if update_data:
            updated_db = await self.career_repository.update(career_db, update_data)
            return self.career_repository.to_domain(updated_db)
        return self.career_repository.to_domain(career_db)

    async def delete(self, career_id: int) -> bool:
        career_db = await self.career_repository.get_by_id(career_id)
        if not career_db:
            return False
        await self.career_repository.delete(career_db)
        return True

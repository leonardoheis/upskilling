from sqlalchemy import select
from sqlalchemy.orm import selectinload

from upskills.domain import Career as CareerDomain
from upskills.repositories.base import BaseRepository

from .models import Career


class CareerRepository(BaseRepository[Career]):
    async def get_by_id(self, id_value: int, id_column: str = "career_id") -> Career | None:
        async with self._db_provider.session() as session:
            stmt = select(Career).options(selectinload(Career.path_templates)).where(Career.career_id == id_value)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_all_with_paths(self, *, skip: int = 0, limit: int = 100) -> list[Career]:
        async with self._db_provider.session() as session:
            stmt = select(Career).options(selectinload(Career.path_templates)).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    @staticmethod
    def to_domain(career: Career, *, include_paths: bool = False) -> CareerDomain:
        career_dict = career.to_dict()
        if not include_paths and "path_templates" in career_dict:
            career_dict.pop("path_templates")
        return CareerDomain.model_validate(career_dict)

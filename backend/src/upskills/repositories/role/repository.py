from sqlalchemy import select

from upskills.repositories.base import BaseRepository
from upskills.repositories.user.models import Role


class RoleRepository(BaseRepository[Role]):
    async def get_by_id(self, id_value: int, id_column: str = "role_id") -> Role | None:
        return await super().get_by_id(id_value, "role_id")

    async def get_by_name(self, name: str) -> Role | None:
        async with self._db_provider.session() as session:
            stmt = select(Role).where(Role.name == name)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

from typing import Any, TypeVar, cast, get_args

from dependency_injector.wiring import Provide, inject
from pydantic import BaseModel
from sqlalchemy import exists as sql_exists
from sqlalchemy import select
from sqlalchemy.sql.functions import count

from upskills.db import DatabaseProvider

from .models import Base

ModelT = TypeVar("ModelT", bound=Base)


def _to_dict(data: dict[str, Any] | BaseModel, *, exclude_unset: bool = False) -> dict[str, Any]:
    if isinstance(data, dict):
        return data
    if hasattr(data, "model_dump"):
        return data.model_dump(exclude_unset=exclude_unset)
    msg = f"Expected dict or Pydantic model, got {type(data)}"
    raise TypeError(msg)


class BaseRepository[ModelT: Base]:
    @inject
    def __init__(
        self,
        db_provider: DatabaseProvider = Provide["db_provider"],
    ) -> None:
        self._db_provider = db_provider

    @property
    def _model(self) -> type[ModelT]:
        orig_bases = getattr(self.__class__, "__orig_bases__", ())
        if not orig_bases:
            msg = f"Could not determine model type for {self.__class__.__name__}"
            raise RuntimeError(msg)
        args = get_args(orig_bases[0])
        if args:
            return cast("type[ModelT]", args[0])
        msg = f"Could not determine model type for {self.__class__.__name__}"
        raise RuntimeError(msg)

    async def get_by_id(self, id_value: int, id_column: str = "id") -> ModelT | None:
        async with self._db_provider.session() as session:
            column = getattr(self._model, id_column)
            stmt = select(self._model).where(column == id_value)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        descending: bool = False,
    ) -> list[ModelT]:
        async with self._db_provider.session() as session:
            stmt = select(self._model)

            if order_by:
                column = getattr(self._model, order_by)
                stmt = stmt.order_by(column.desc() if descending else column)

            stmt = stmt.offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def count(self) -> int:
        async with self._db_provider.session() as session:
            stmt = select(count()).select_from(self._model)  # pylint: disable=no-member E1101
            result = await session.execute(stmt)
            return result.scalar() or 0

    async def create(self, data: dict[str, Any] | BaseModel) -> ModelT:
        data_dict = _to_dict(data)
        async with self._db_provider.session() as session:
            instance = self._model(**data_dict)
            session.add(instance)
            await session.flush()
            await session.refresh(instance)
            await session.commit()
            return instance

    async def update(
        self,
        instance: ModelT,
        data: dict[str, Any] | BaseModel,
    ) -> ModelT:
        data_dict = _to_dict(data, exclude_unset=True)
        async with self._db_provider.session() as session:
            instance = await session.merge(instance)
            for key, value in data_dict.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            await session.flush()
            await session.refresh(instance)
            await session.commit()
            return instance

    async def delete(self, instance: ModelT) -> None:
        async with self._db_provider.session() as session:
            instance = await session.merge(instance)
            await session.delete(instance)
            await session.flush()
            await session.commit()

    async def exists(self, **kwargs: Any) -> bool:
        async with self._db_provider.session() as session:
            conditions = [getattr(self._model, key) == value for key, value in kwargs.items()]
            stmt = select(sql_exists().where(*conditions))
            result = await session.execute(stmt)
            return result.scalar() or False

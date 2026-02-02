"""Base repository with common CRUD operations."""

from typing import Any, TypeVar, get_args

from dependency_injector.wiring import Provide, inject
from sqlalchemy import select

from upskills.db.provider import DatabaseProvider
from upskills.models.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository[ModelType: Base]:
    """Base repository providing common CRUD operations.

    This follows the Repository pattern to abstract data access logic.
    Each method uses a session from the DatabaseProvider with automatic
    transaction management.
    """

    @inject
    def __init__(
        self,
        db_provider: DatabaseProvider = Provide["db_provider"],
    ) -> None:
        """Initialize the repository.

        Args:
            db_provider: The database provider (injected).
        """
        self._db_provider = db_provider

    @property
    def _model(self) -> type[ModelType]:
        """Extract the model type from the generic type parameter.

        Returns:
            The model class for this repository.
        """
        # Get the first base class (should be BaseRepository[SomeModel])
        base = self.__class__.__orig_bases__[0]
        # Extract the type arguments from the generic
        args = get_args(base)
        if args:
            return args[0]
        msg = f"Could not determine model type for {self.__class__.__name__}"
        raise RuntimeError(msg)

    async def get_by_id(self, id_value: int, id_column: str = "id") -> ModelType | None:
        """Get a single record by its primary key.

        Args:
            id_value: The primary key value.
            id_column: The name of the primary key column.

        Returns:
            The model instance or None if not found.
        """
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
    ) -> list[ModelType]:
        """Get all records with optional pagination and ordering.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            order_by: Column name to order by.
            descending: Whether to sort in descending order.

        Returns:
            List of model instances.
        """
        async with self._db_provider.session() as session:
            stmt = select(self._model)

            if order_by:
                column = getattr(self._model, order_by)
                stmt = stmt.order_by(column.desc() if descending else column)

            stmt = stmt.offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def count(self) -> int:
        """Get the total count of records.

        Returns:
            The total number of records.
        """
        from sqlalchemy import func

        async with self._db_provider.session() as session:
            stmt = select(func.count()).select_from(self._model)
            result = await session.execute(stmt)
            return result.scalar() or 0

    async def create(self, data: dict[str, Any]) -> ModelType:
        """Create a new record.

        Args:
            data: Dictionary of column values.

        Returns:
            The created model instance.
        """
        async with self._db_provider.session() as session:
            instance = self._model(**data)
            session.add(instance)
            await session.flush()
            await session.refresh(instance)
            await session.commit()
            return instance

    async def update(
        self,
        instance: ModelType,
        data: dict[str, Any],
    ) -> ModelType:
        """Update an existing record.

        Args:
            instance: The model instance to update.
            data: Dictionary of column values to update.

        Returns:
            The updated model instance.
        """
        async with self._db_provider.session() as session:
            # Merge the instance into the new session
            instance = await session.merge(instance)
            for key, value in data.items():
                if hasattr(instance, key) and value is not None:
                    setattr(instance, key, value)
            await session.flush()
            await session.refresh(instance)
            await session.commit()
            return instance

    async def delete(self, instance: ModelType) -> None:
        """Delete a record.

        Args:
            instance: The model instance to delete.
        """
        async with self._db_provider.session() as session:
            # Merge the instance into the new session
            instance = await session.merge(instance)
            await session.delete(instance)
            await session.flush()
            await session.commit()

    async def exists(self, **kwargs: Any) -> bool:
        """Check if a record exists with the given criteria.

        Args:
            **kwargs: Column-value pairs to filter by.

        Returns:
            True if a matching record exists.
        """
        from sqlalchemy import exists as sql_exists

        async with self._db_provider.session() as session:
            conditions = [getattr(self._model, key) == value for key, value in kwargs.items()]
            stmt = select(sql_exists().where(*conditions))
            result = await session.execute(stmt)
            return result.scalar() or False

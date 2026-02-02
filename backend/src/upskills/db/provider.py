"""Abstract database provider interface."""

from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager

from sqlalchemy.ext.asyncio import AsyncSession


class DatabaseProvider(ABC):
    """Abstract base class for database providers.

    This interface allows swapping database implementations (SQLite, PostgreSQL)
    and makes the database layer mockable for testing.
    """

    @abstractmethod
    async def init_db(self) -> None:
        """Initialize the database (create tables if needed)."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close all database connections."""
        ...

    @abstractmethod
    def session(self) -> AbstractAsyncContextManager[AsyncSession]:
        """Provide a transactional scope around a series of operations.

        Usage:
            async with provider.session() as session:
                # perform database operations
                await session.commit()
        """
        ...

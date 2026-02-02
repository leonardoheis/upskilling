"""SQLite database provider implementation."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from upskills.db.provider import DatabaseProvider
from upskills.models.db.base import Base


class SQLiteProvider(DatabaseProvider):
    """SQLite implementation of the database provider.

    This provider uses aiosqlite for async SQLite operations.
    """

    def __init__(self, db_path: str) -> None:
        """Initialize the SQLite provider.

        Args:
            db_path: Path to the SQLite database file.
        """
        self._db_path = db_path
        self._engine: AsyncEngine = create_async_engine(
            f"sqlite+aiosqlite:///{db_path}",
            echo=False,
            future=True,
        )
        self._session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    async def init_db(self) -> None:
        """Initialize the database by creating all tables."""
        # Ensure the directory exists
        db_dir = Path(self._db_path).parent
        if db_dir and not db_dir.exists():
            db_dir.mkdir(parents=True, exist_ok=True)

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        """Close the database engine and all connections."""
        await self._engine.dispose()

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Provide a transactional scope around a series of operations.

        Yields:
            AsyncSession: Database session for operations.
        """
        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

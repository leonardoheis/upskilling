from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from upskills.repositories.base.models import Base

from .provider import DatabaseProvider


class SQLiteProvider(DatabaseProvider):
    def __init__(self, db_path: str) -> None:
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
        db_dir = Path(self._db_path).parent
        if db_dir and not db_dir.exists():
            db_dir.mkdir(parents=True, exist_ok=True)

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        await self._engine.dispose()

    def session(self) -> AbstractAsyncContextManager[AsyncSession]:
        @asynccontextmanager
        async def _session() -> AsyncIterator[AsyncSession]:
            db_session = self._session_factory()
            try:
                yield db_session
                await db_session.commit()
            except Exception:
                await db_session.rollback()
                raise
            finally:
                await db_session.close()

        return _session()

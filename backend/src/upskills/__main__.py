import asyncio

from .api import server_factory


async def main() -> None:
    server = server_factory()
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())

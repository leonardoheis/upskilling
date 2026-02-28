from uvicorn import Config, Server

from upskills.core import get_settings

from .app import app_factory


def server_factory() -> Server:
    settings = get_settings()

    config = Config(
        app=app_factory,
        host=settings.server_host,
        port=settings.server_port,
        log_level="info",
        factory=True,
    )
    return Server(config)

__all__ = ["lifespan"]

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import api_settings
from src.storage.sql import SQLAlchemyStorage


async def setup_repositories() -> SQLAlchemyStorage:
    from src.repositories.users.repository import user_repository
    from src.repositories.bookings.repository import booking_repository
    from src.repositories.auth.repository import auth_repository
    from src.repositories.innohassle_accounts import innohassle_accounts

    storage = SQLAlchemyStorage.from_url(api_settings.db_url)
    user_repository.update_storage(storage)
    booking_repository.update_storage(storage)
    auth_repository.update_storage(storage)

    await innohassle_accounts.update_key_set()

    return storage


def setup_timezone():
    import sys
    import os
    import time

    if sys.platform != "win32":  # unix only
        os.environ["TZ"] = "Europe/Moscow"
        time.tzset()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Application startup
    storage = await setup_repositories()
    yield
    # Application shutdown
    await storage.close_connection()

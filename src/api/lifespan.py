__all__ = ["lifespan"]

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.use_cases.notifications import notification_use_case
from src.config import api_settings
from src.storage.sql import SQLAlchemyStorage


async def setup_repositories() -> SQLAlchemyStorage:
    from src.repositories.auth.repository import auth_repository
    from src.repositories.bookings.repository import booking_repository
    from src.repositories.innohassle_accounts import innohassle_accounts
    from src.repositories.users.repository import user_repository

    storage = SQLAlchemyStorage.from_url(api_settings.db_url)
    user_repository.update_storage(storage)
    booking_repository.update_storage(storage)
    auth_repository.update_storage(storage)

    await innohassle_accounts.update_key_set()

    return storage


async def booking_notifications_loop() -> None:
    while True:
        await notification_use_case.notify_users_about_upcoming_bookings()
        await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Application startup
    storage = await setup_repositories()
    asyncio.create_task(booking_notifications_loop())
    yield
    # Application shutdown
    await storage.close_connection()

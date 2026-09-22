__all__ = ["lifespan"]

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.logging_ import logger
from src.api.use_cases.notifications import notification_use_case
from src.config import api_settings
from src.storage.sql import SQLAlchemyStorage


async def setup_repositories() -> SQLAlchemyStorage:
    from src.repositories.auth.repository import auth_repository
    from src.repositories.bookings.repository import booking_repository
    from src.repositories.inh_accounts_sdk import inh_accounts
    from src.repositories.users.repository import user_repository

    storage = SQLAlchemyStorage.from_url(api_settings.db_url)
    user_repository.update_storage(storage)
    booking_repository.update_storage(storage)
    auth_repository.update_storage(storage)

    await inh_accounts.update_key_set()

    return storage


async def booking_notifications_loop() -> None:
    while True:
        try:
            await notification_use_case.notify_users_about_upcoming_bookings()
        except Exception as e:
            logger.error(f"Error in notification loop: {e}", exc_info=True)
        await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Application startup
    storage = await setup_repositories()

    # Pre-warm Prefect ephemeral server so it's ready before the notification loop
    # fires its first @flow call (avoids startup timeout / port-collision race).
    try:
        from prefect.client.orchestration import get_client

        async with get_client() as client:  # noqa: F841
            logger.info("Prefect ephemeral server initialized")
    except Exception as e:
        logger.warning(f"Failed to pre-warm Prefect server: {e}")

    asyncio.create_task(booking_notifications_loop())
    yield
    # Application shutdown
    await storage.close_connection()

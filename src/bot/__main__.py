import asyncio

from aiogram import Bot, F
from aiogram import types
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.types import ErrorEvent
from aiogram_dialog import setup_dialogs
from aiogram_dialog.api.exceptions import UnknownIntent

import src.bot.logging_  # noqa: F401
from src.bot.constants import (
    bot_name,
    bot_description,
    bot_short_description,
    bot_commands,
)
from src.bot.dispatcher import CustomDispatcher
from src.bot.middlewares import LogAllEventsMiddleware
from src.config import bot_settings

bot = Bot(token=bot_settings.bot_token.get_secret_value())
if bot_settings.redis_url:
    storage = RedisStorage.from_url(
        bot_settings.redis_url.get_secret_value(), key_builder=DefaultKeyBuilder(with_destiny=True)
    )
else:
    storage = MemoryStorage()
dp = CustomDispatcher(storage=storage)
log_all_events_middleware = LogAllEventsMiddleware()
dp.message.middleware(log_all_events_middleware)
dp.callback_query.middleware(log_all_events_middleware)


@dp.error(ExceptionTypeFilter(UnknownIntent), F.update.callback_query.as_("callback_query"))
async def unknown_intent_handler(event: ErrorEvent, callback_query: types.CallbackQuery):
    await callback_query.answer("Unknown intent: Please, try to restart the action.")


from src.bot.routers.registration import router as router_registration  # noqa: E402
from src.bot.routers.start_help_menu import router as start_help_menu_router  # noqa: E402
from src.bot.routers.admin import router as router_admin  # noqa: E402
from src.bot.routers.booking import router as router_bookings  # noqa: E402
from src.bot.routers.schedule import router as router_image_schedule  # noqa: E402

dp.include_router(router_registration)  # sink for not registered users
dp.include_router(start_help_menu_router)  # start, help, menu commands
dp.include_router(router_admin)  # admin commands
dp.include_router(router_bookings)  # everything about bookings (create, show, etc.)
dp.include_router(router_image_schedule)  # schedule commands (show image)

setup_dialogs(dp)


async def main():
    # Set bot name, description and commands
    existing_bot = {
        "name": (await bot.get_my_name()).name,
        "description": (await bot.get_my_description()).description,
        "shortDescription": (await bot.get_my_short_description()).short_description,
        "commands": await bot.get_my_commands(),
    }

    if existing_bot["name"] != bot_name:
        await bot.set_my_name(bot_name)
    if existing_bot["description"] != bot_description:
        await bot.set_my_description(bot_description)
    if existing_bot["shortDescription"] != bot_short_description:
        await bot.set_my_short_description(bot_short_description)
    if existing_bot["commands"] != bot_commands:
        await bot.set_my_commands(bot_commands)
    # Drop pending updates
    await bot.delete_webhook(drop_pending_updates=True)
    # Start long-polling
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


# NOTE: No need for if __name__ == "__main__":, because this is the __main__.py module already
asyncio.run(main())

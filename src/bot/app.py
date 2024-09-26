import asyncio
import datetime

import pytz
from aiogram import Bot, F, types
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram.types import BufferedInputFile, ErrorEvent
from aiogram_dialog import setup_dialogs
from aiogram_dialog.api.exceptions import UnknownIntent

import src.bot.logging_  # noqa: F401
from src.bot.api import api_client
from src.bot.constants import bot_commands, bot_description, bot_name, bot_short_description
from src.bot.dispatcher import CustomDispatcher
from src.bot.logging_ import logger
from src.bot.middlewares import LogAllEventsMiddleware
from src.config import bot_settings, settings

bot = Bot(token=bot_settings.bot_token.get_secret_value())
if bot_settings.redis_url:
    storage = RedisStorage.from_url(
        bot_settings.redis_url.get_secret_value(), key_builder=DefaultKeyBuilder(with_destiny=True)
    )
    logger.info("Using Redis storage")
else:
    storage = MemoryStorage()
    logger.info("Using Memory storage")
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


async def receptionist_notifications_loop():
    if not settings.bot_settings.users or not settings.bot_settings.notification_time:
        return
    while True:
        current_date = datetime.datetime.now(datetime.UTC)
        planned_date = datetime.datetime(
            current_date.year,
            current_date.month,
            current_date.day,
            settings.bot_settings.notification_time.hour,
            settings.bot_settings.notification_time.minute,
            tzinfo=pytz.UTC,
        )
        days_until_monday = (7 - current_date.weekday()) % 7
        planned_date += datetime.timedelta(days=days_until_monday)
        if planned_date < current_date:
            planned_date += datetime.timedelta(days=7)
        await asyncio.sleep((planned_date - current_date).seconds)
        for telegram_id in settings.bot_settings.users:
            while True:
                # noinspection PyBroadException
                try:
                    response = await api_client.export_users_as_bot()
                    if response:
                        bytes_, filename = response
                        document = BufferedInputFile(bytes_, filename)
                        await bot.send_document(telegram_id, document, caption="Here is the list of users.")
                    else:
                        raise RuntimeError("Response was None")
                    break
                except:  # noqa: E722
                    logger.warning("Something went wrong. Please check.")
                    pass


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
    await receptionist_notifications_loop()
    # Start long-polling
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

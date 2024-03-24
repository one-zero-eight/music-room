import asyncio

from aiogram import Bot, F
from aiogram import types
from aiogram.filters import Command, ExceptionTypeFilter, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.types import ErrorEvent
from aiogram_dialog import setup_dialogs
from aiogram_dialog.api.exceptions import UnknownIntent

import src.bot.logging_  # noqa: F401
from src.bot.constants import (
    instructions_url,
    how_to_get_url,
    tg_chat_url,
    bot_name,
    bot_description,
    bot_short_description,
    bot_commands,
)
from src.bot.dispatcher import CustomDispatcher
from src.bot.filters import RegisteredUserFilter, FilledProfileFilter
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


@dp.message(CommandStart(), ~RegisteredUserFilter())
async def start(message: types.Message):
    from src.bot.routers.registration.keyboards import registration_kb

    await message.answer("Welcome! To continue, you need to register.", reply_markup=registration_kb)


@dp.message(CommandStart(), FilledProfileFilter())
async def start_but_registered(message: types.Message):
    from src.bot.menu import menu_kb

    await message.answer("Welcome! Choose the action you're interested in.", reply_markup=menu_kb)


@dp.message(Command("help"))
async def help_handler(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Instructions", url=instructions_url),
                types.InlineKeyboardButton(text="Location", url=how_to_get_url),
                types.InlineKeyboardButton(text="Telegram chat", url=tg_chat_url),
            ]
        ]
    )

    await message.answer(
        "If you have any questions, you can ask them in the chat or read the instructions.",
        reply_markup=keyboard,
    )


@dp.message(Command("menu"), FilledProfileFilter())
async def menu_handler(message: types.Message):
    from src.bot.menu import menu_kb

    await message.answer("Choose the action you're interested in.", reply_markup=menu_kb)


from src.bot.routers import routers  # noqa: E402

for router in routers:
    dp.include_router(router)
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


if __name__ == "__main__":
    asyncio.run(main())

from aiogram import Router
from aiogram import types
from aiogram.filters import Command, CommandStart

from src.bot.constants import instructions_url, how_to_get_url, tg_chat_url

router = Router(name="start_help_menu")


@router.message(CommandStart())
async def start(message: types.Message):
    from src.bot.menu import menu_kb

    await message.answer("Welcome! Choose the action you're interested in.", reply_markup=menu_kb)


@router.message(Command("help"))
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
        "If you have any questions, you can ask them in the chat or read the instructions.", reply_markup=keyboard
    )


@router.message(Command("menu"))
async def menu_handler(message: types.Message):
    from src.bot.menu import menu_kb

    await message.answer("Choose the action you're interested in.", reply_markup=menu_kb)

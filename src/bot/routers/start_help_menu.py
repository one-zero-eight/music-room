from aiogram import Router, types
from aiogram.filters import Command, CommandStart

from src.bot.menu import help_kb

router = Router(name="start_help_menu")


@router.message(CommandStart())
async def start(message: types.Message):
    from src.bot.menu import menu_kb

    await message.answer("Welcome! Choose the action you're interested in.", reply_markup=menu_kb)


@router.message(Command("help"))
async def help_handler(message: types.Message):
    await message.answer(
        "If you have any questions, you can ask them in the chat or read the instructions.",
        reply_markup=help_kb,
    )


@router.message(Command("menu"))
async def menu_handler(message: types.Message):
    from src.bot.menu import menu_kb

    await message.answer("Choose the action you're interested in.", reply_markup=menu_kb)

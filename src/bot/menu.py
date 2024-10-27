from aiogram import types
from aiogram.utils.i18n import gettext as _

from src.bot import constants


def get_menu_kb() -> types.ReplyKeyboardMarkup:
    menu_kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                types.KeyboardButton(text=str(constants.create_booking_message)),
                types.KeyboardButton(text=str(constants.my_bookings_message)),
            ],
            [
                types.KeyboardButton(text=str(constants.image_schedule_message)),
            ],
        ],
    )
    return menu_kb


def get_help_kb() -> types.InlineKeyboardMarkup:
    help_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text=_("Instructions"), url=constants.instructions_url),
                types.InlineKeyboardButton(text=_("Location"), url=constants.how_to_get_url),
            ],
            [
                types.InlineKeyboardButton(text=_("Telegram chat"), url=constants.tg_chat_url),
            ],
        ]
    )
    return help_kb

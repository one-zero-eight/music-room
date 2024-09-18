from aiogram import types

from src.bot import constants

menu_kb = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            types.KeyboardButton(text=constants.create_booking_message),
            types.KeyboardButton(text=constants.my_bookings_message),
        ],
        [
            types.KeyboardButton(text=constants.image_schedule_message),
        ],
    ],
)

help_kb = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            types.InlineKeyboardButton(text="Instructions", url=constants.instructions_url),
            types.InlineKeyboardButton(text="Location", url=constants.how_to_get_url),
        ],
        [
            types.InlineKeyboardButton(text="Telegram chat", url=constants.tg_chat_url),
        ],
    ]
)

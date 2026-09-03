from aiogram import Router, types
from aiogram.filters.callback_data import CallbackData

from src.bot import constants
from src.bot.api import api_client
from src.bot.validators import is_english_name

router = Router(name="poll")


class StillUsingPollCallbackData(CallbackData, prefix="still_using_poll"):
    answer: str  # "yes" / "no"


def build_still_using_keyboard() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Да", callback_data=StillUsingPollCallbackData(answer="yes").pack()),
                types.InlineKeyboardButton(text="Нет", callback_data=StillUsingPollCallbackData(answer="no").pack()),
            ]
        ]
    )


@router.callback_query(StillUsingPollCallbackData.filter())
async def handle_still_using_answer(callback_query: types.CallbackQuery, callback_data: StillUsingPollCallbackData):
    is_using = callback_data.answer == "yes"
    await api_client.submit_still_using_answer(callback_query.from_user.id, is_using)
    await callback_query.answer()
    await callback_query.message.edit_text(
        constants.still_using_poll_ack_yes if is_using else constants.still_using_poll_ack_no
    )

    if is_using:
        user = await api_client.get_me(callback_query.from_user.id)
        if user and is_english_name(user.name):
            await callback_query.message.answer(constants.russian_name_reminder_message)

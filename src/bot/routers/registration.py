import asyncio

from aiogram import Router, Bot
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.state import any_state
from aiogram.types import Message, LoginUrl

from src.bot.constants import rules_confirmation_message
from src.bot.filters import RegisteredUserFilter, EmptyUsernameFilter
from src.bot.menu import menu_kb, help_kb
from src.config import settings

router = Router(name="registration")


class RegistrationStates(StatesGroup):
    rules_confirmation_requested = State()


@router.message(any_state, ~EmptyUsernameFilter())
@router.callback_query(any_state, ~EmptyUsernameFilter())
async def empty_username(_, bot: Bot, state: FSMContext, event_from_user: types.User):
    await bot.send_message(
        event_from_user.id,
        "To continue, you need to fill in your telegram username",
    )


@router.message(any_state, ~RegisteredUserFilter())
@router.callback_query(any_state, ~RegisteredUserFilter())
async def not_registered(_, bot: Bot, state: FSMContext, event_from_user: types.User):
    from src.bot.api import api_client

    bot_name = (await bot.me()).username
    is_new_user, detail = await api_client.start_registration(event_from_user.id)

    if is_new_user is None:
        connect_kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Connect",
                        login_url=LoginUrl(
                            url=settings.accounts.telegram_login_url + f"?bot={bot_name}",
                            forward_text="Connect your telegram",
                            bot_username=settings.accounts.telegram_bot_username,
                        ),
                    )
                ]
            ]
        )
        push_kb = types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(
                        text="I have connected telegram to InNoHassle account.",
                    )
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

        await bot.send_message(
            event_from_user.id,
            "To continue, you need to connect your Telegram account to the InNoHassle account.",
            reply_markup=connect_kb,
        )
        # wait for the user to connect the account
        await asyncio.sleep(3)
        await bot.send_message(
            event_from_user.id,
            "If you have already connected your account, just press the button.",
            reply_markup=push_kb,
        )
    elif is_new_user is False:
        from src.bot.menu import menu_kb

        await bot.send_message(
            event_from_user.id, "Welcome! Choose the action you're interested in.", reply_markup=menu_kb
        )
    elif is_new_user is True:
        from src.bot.constants import rules_confirmation_message, rules_message

        confirm_kb = types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(
                        text=rules_confirmation_message,
                    )
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await state.set_state(RegistrationStates.rules_confirmation_requested)
        await bot.send_message(event_from_user.id, rules_message, reply_markup=confirm_kb)


@router.message(RegistrationStates.rules_confirmation_requested)
async def confirm_rules(message: Message, state: FSMContext):
    if message.text[:100] == rules_confirmation_message.format(name=(await state.get_data()))[:100]:
        text = (
            "You have successfully registered.\n\n"
            "❗️ Access to the Sports Complex will appear after submitting the list of users (usually on "
            "Monday)."
        )

        await message.answer(text, reply_markup=menu_kb, parse_mode="HTML")

        await message.answer(
            "If you have any questions, you can ask them in the chat or read the instructions.",
            reply_markup=help_kb,
        )

        await state.clear()
    else:
        await message.answer("You haven't confirmed the rules. Please, try again.")

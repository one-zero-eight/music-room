import asyncio

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, any_state
from aiogram.types import LoginUrl, Message
from aiogram.utils.i18n import gettext as _

from src.bot.constants import rules_confirmation_message
from src.bot.filters import EmptyUsernameFilter, RegisteredUserFilter
from src.bot.menu import get_help_kb, get_menu_kb
from src.bot.validators import is_russian_name
from src.config import settings

router = Router(name="registration")


class RegistrationStates(StatesGroup):
    rules_confirmation_requested = State()
    russian_name_requested = State()


@router.message(any_state, ~EmptyUsernameFilter())
@router.callback_query(any_state, ~EmptyUsernameFilter())
async def empty_username(__, bot: Bot, state: FSMContext, event_from_user: types.User):
    await bot.send_message(
        event_from_user.id,
        _("To continue, you need to fill in your telegram username"),
    )


@router.message(any_state, ~RegisteredUserFilter())
@router.callback_query(any_state, ~RegisteredUserFilter())
async def not_registered(__, bot: Bot, state: FSMContext, event_from_user: types.User):
    from src.bot.api import api_client

    bot_name = (await bot.me()).username
    is_new_user, detail = await api_client.start_registration(event_from_user.id)

    if is_new_user is None:
        connect_kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text=_("Connect"),
                        login_url=LoginUrl(
                            url=settings.accounts.telegram_login_url + f"?bot={bot_name}",
                            forward_text=_("Connect your telegram"),
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
                        text=_("I have connected telegram to InNoHassle account."),
                    )
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

        await bot.send_message(
            event_from_user.id,
            _("To continue, you need to connect your Telegram account to the InNoHassle account."),
            reply_markup=connect_kb,
        )
        # wait for the user to connect the account
        await asyncio.sleep(3)
        await bot.send_message(
            event_from_user.id,
            _("If you have already connected your account, just press the button."),
            reply_markup=push_kb,
        )
    elif is_new_user is False:
        from src.bot.menu import get_menu_kb

        await bot.send_message(
            event_from_user.id, _("Welcome! Choose the action you're interested in."), reply_markup=get_menu_kb()
        )
    elif is_new_user is True:
        from src.bot.constants import rules_confirmation_message, rules_message

        confirm_kb = types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(
                        text=str(rules_confirmation_message),
                    )
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await state.set_state(RegistrationStates.rules_confirmation_requested)
        await bot.send_message(event_from_user.id, str(rules_message), reply_markup=confirm_kb)


@router.message(RegistrationStates.rules_confirmation_requested)
async def confirm_rules(message: Message, state: FSMContext):
    if message.text[:100] == rules_confirmation_message.format(name=(await state.get_data()))[:100]:
        text = _(
            "You have successfully registered.\n\n"
            "❗️ Access to the Sports Complex will appear after submitting the list of users (usually on "
            "Monday)."
        )

        await message.answer(text, reply_markup=get_menu_kb(), parse_mode="HTML")

        await message.answer(
            _("If you have any questions, you can ask them in the chat or read the instructions."),
            reply_markup=get_help_kb(),
        )
        await state.clear()
    else:
        await message.answer(_("You haven't confirmed the rules. Please, try again."))


# A registered user without a Russian name is asked for one only when they try to book
# (see `start_booking`); viewing bookings and other read-only actions stay available.
# Commands (/menu, /my_bookings, ...) are let through so the user is never trapped here.
@router.message(RegistrationStates.russian_name_requested, ~F.text.startswith("/"))
async def set_russian_name(message: Message, bot: Bot, state: FSMContext, event_from_user: types.User):
    from src.bot.api import api_client

    name = (message.text or "").strip()
    if not is_russian_name(name):
        await bot.send_message(
            event_from_user.id,
            _("Please write your full name (first and last name) in Russian, using Cyrillic letters only."),
        )
        return

    me = await api_client.get_me(event_from_user.id)
    alias = me.alias if me and me.alias else event_from_user.username
    ok, detail = await api_client.fill_profile(event_from_user.id, name=name, alias=alias)
    if not ok:
        await bot.send_message(
            event_from_user.id,
            _("Something went wrong while saving your name. Please try again later."),
        )
        return

    await state.clear()
    await bot.send_message(
        event_from_user.id,
        _("Thank you! Your name has been saved, you can now create a booking."),
        reply_markup=get_menu_kb(),
    )

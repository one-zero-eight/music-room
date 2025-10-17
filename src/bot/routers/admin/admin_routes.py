from typing import Any

from aiogram import Bot, types
from aiogram.filters import Command, Filter
from aiogram.fsm.state import any_state
from aiogram.types import BotCommandScopeChat, BufferedInputFile, TelegramObject, User
from aiogram.utils.i18n import gettext as _
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Cancel, Group, Select
from aiogram_dialog.widgets.text import Const, Format

from src.bot.api import api_client
from src.bot.constants import admin_commands, bot_commands
from src.bot.i18n import I18NFormat
from src.bot.routers.admin import router
from src.bot.routers.admin.states import ChangeStatusStates
from src.schemas import UserStatus


class StatusFilter(Filter):
    _status: list[UserStatus]

    def __init__(self, status: list[UserStatus] | None = None):
        self._status = status

    async def __call__(self, event: TelegramObject, event_from_user: User) -> bool | dict[str, Any]:
        telegram_id = event_from_user.id
        user = await api_client.get_me(telegram_id=telegram_id)
        if self._status is None:
            return {"status": user.status}

        if user.status in self._status:
            return True
        return False


@router.message(Command("admin"), StatusFilter([UserStatus.LORD, UserStatus.ADMIN]))
async def enable_admin_mode(message: types.Message, bot: Bot):
    text = _("You are the Lord of the Music Room! You can use the following commands:")

    for command in admin_commands:
        text += f"\n{command.command} - {command.description}"

    await message.answer(text)
    await bot.set_my_commands(
        bot_commands + admin_commands,
        scope=BotCommandScopeChat(chat_id=message.from_user.id),
    )


@router.message(Command("export_users"), StatusFilter([UserStatus.LORD, UserStatus.ADMIN]))
async def export_users(message: types.Message):
    response = await api_client.export_users(message.from_user.id)
    if response:
        bytes_, filename = response
        document = BufferedInputFile(bytes_, filename)
        await message.answer_document(document, caption=_("Here is the list of users."))
    else:
        await message.answer(_("Failed to export users."))


@router.message(any_state, Command("change_status"), StatusFilter([UserStatus.ADMIN]))
async def change_status(_message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        ChangeStatusStates.input_username,
        mode=StartMode.RESET_STACK,
    )


async def on_username_input(message: types.Message, _widget: TextInput, dialog_manager: DialogManager, username: str):
    username = username.lstrip("@")
    user = await api_client.get_user(message.from_user.id, alias=username)
    if not user:
        await message.answer(_("User not found. Please try again"))
        return

    dialog_manager.dialog_data["username"] = username
    dialog_manager.dialog_data["user_tg_id"] = user.telegram_id
    dialog_manager.dialog_data["current_status"] = user.status

    await dialog_manager.next()


async def on_status_selected(
    callback: types.CallbackQuery, _widget: Select, dialog_manager: DialogManager, new_status: str
):
    user_tg_id = dialog_manager.dialog_data["user_tg_id"]

    success = await api_client.set_user_status_as_bot(
        telegram_id=user_tg_id,
        status=UserStatus(new_status),
    )

    if success:
        await callback.message.answer(
            _("✅ Successfully updated status for @{username}").format(username=dialog_manager.dialog_data["username"])
        )
    else:
        await callback.message.answer(_("❌ Failed to update user status"))

    await dialog_manager.done()


async def get_dialog_data(dialog_manager, **kwargs):
    return dialog_manager.dialog_data


username_window = Window(
    I18NFormat("Please enter the username of the user whose status you want to change:"),
    TextInput(id="username", on_success=on_username_input),
    Cancel(Const("❌")),
    state=ChangeStatusStates.input_username,
)

status_window = Window(
    I18NFormat("Select new status for @{username}\nCurrent status: {current_status}"),
    Group(
        Select(
            items=[(status.value, status.value) for status in UserStatus],
            id="status_selector",
            item_id_getter=lambda x: x[0],
            text=Format("{item[0]}"),
            on_click=on_status_selected,
        ),
        width=2,
    ),
    Cancel(Const("❌")),
    state=ChangeStatusStates.select_status,
    getter=get_dialog_data,
)

change_status_dialog = Dialog(username_window, status_window)

router.include_router(change_status_dialog)

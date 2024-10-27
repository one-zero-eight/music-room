from typing import Any

from aiogram import Bot, Router, types
from aiogram.filters import Command, Filter
from aiogram.types import BotCommandScopeChat, BufferedInputFile, TelegramObject, User
from aiogram.utils.i18n import gettext as _

from src.bot.api import UserStatus, api_client
from src.bot.constants import admin_commands, bot_commands

router = Router(name="admin")


class StatusFilter(Filter):
    _status: UserStatus

    def __init__(self, status: UserStatus | None = None):
        self._status = status

    async def __call__(self, event: TelegramObject, event_from_user: User) -> bool | dict[str, Any]:
        telegram_id = event_from_user.id
        user = await api_client.get_me(telegram_id=telegram_id)
        if self._status is None:
            return {"status": user.status}

        if user.status == self._status:
            return True
        return False


@router.message(Command("admin"), StatusFilter(UserStatus.LORD))
async def enable_admin_mode(message: types.Message, bot: Bot):
    text = _("You are the Lord of the Music Room! You can use the following commands:")

    for command in admin_commands:
        text += f"\n{command.command} - {command.description}"

    await message.answer(text)
    await bot.set_my_commands(
        bot_commands + admin_commands,
        scope=BotCommandScopeChat(chat_id=message.from_user.id),
    )


@router.message(Command("export_users"), StatusFilter(UserStatus.LORD))
async def export_users(message: types.Message):
    response = await api_client.export_users(message.from_user.id)
    if response:
        bytes_, filename = response
        document = BufferedInputFile(bytes_, filename)
        await message.answer_document(document, caption=_("Here is the list of users."))
    else:
        await message.answer(_("Failed to export users."))

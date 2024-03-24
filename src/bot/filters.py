from typing import Any

from aiogram.filters import Filter
from aiogram.types import User, TelegramObject

from src.bot.api import api_client


class RegisteredUserFilter(Filter):
    async def __call__(self, event: TelegramObject, event_from_user: User) -> bool | dict[str, Any]:
        telegram_id = event_from_user.id
        api_user_id = await api_client.get_user_id(telegram_id)
        if api_user_id is None:
            return False
        return {"api_user_id": api_user_id}

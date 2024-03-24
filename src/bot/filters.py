from typing import Any, ClassVar

from aiogram.filters import Filter
from aiogram.types import User, TelegramObject

from src.bot.api import api_client


class RegisteredUserFilter(Filter):
    _cache: ClassVar[dict[int, int]] = {}

    async def __call__(self, event: TelegramObject, event_from_user: User) -> bool | dict[str, Any]:
        telegram_id = event_from_user.id

        if telegram_id in self._cache:
            api_user_id = self._cache[telegram_id]
        elif await api_client.is_user_exists(telegram_id):
            api_user_id = await api_client.get_user_id(telegram_id)
            self._cache[telegram_id] = api_user_id
        else:
            return False
        return {"api_user_id": api_user_id}

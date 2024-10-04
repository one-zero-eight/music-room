import httpx
from src.config import bot_settings


class TgBotClient:
    api_root_path: str

    def __init__(self, api_url: str):
        self.api_root_path = api_url

    def _create_client(self, /, telegram_id: int | None = None) -> httpx.AsyncClient:
        client = httpx.AsyncClient(base_url=self.api_root_path, timeout=httpx.Timeout(3))
        return client

    async def notify_user_about_booking(self, telegram_id: int) -> None:
        async with self._create_client() as client:
            response = await client.post(self.api_root_path + "/booking/notify", json={"telegram_id": telegram_id})
            if response.status_code != 200:
                await self.notify_user_about_booking(telegram_id)


tg_bot_client = TgBotClient(bot_settings.webhook_host + bot_settings.webhook_secret)

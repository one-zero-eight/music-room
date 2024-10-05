import httpx
from src.config import bot_settings


class TgBotClient:
    api_root_path: str

    def __init__(self, api_url: str):
        self.api_root_path = api_url

    def _create_client(self) -> httpx.AsyncClient:
        auth_header = {"Authorization": f"Bearer {bot_settings.bot_token.get_secret_value()}"}
        client = httpx.AsyncClient(headers=auth_header, base_url=self.api_root_path)
        return client

    async def notify_user_about_booking(self, telegram_id: int) -> None:
        async with self._create_client() as client:
            await client.post(self.api_root_path + "/booking/notify", json={"telegram_id": telegram_id})


tg_bot_client = TgBotClient(bot_settings.webhook_url)

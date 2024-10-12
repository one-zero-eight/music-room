import asyncio

import httpx

from src.api.logging_ import logger
from src.config import bot_settings
from src.schemas.booking import ViewBooking


class TgBotClient:
    api_root_path: str

    def __init__(self, api_url: str):
        self.api_root_path = api_url

    def _create_client(self) -> httpx.AsyncClient:
        auth_header = {"Authorization": f"Bearer {bot_settings.bot_token.get_secret_value()}"}
        client = httpx.AsyncClient(headers=auth_header, base_url=self.api_root_path)
        return client

    async def notify_user_about_booking(self, telegram_id: int, booking: ViewBooking) -> None:
        async with self._create_client() as client:
            status_code = 0
            base_log_message = f"Notification webhook booking(id={booking.id}), user(id={telegram_id})"
            while True:
                logger.info(f"{base_log_message} sent")
                try:
                    response = await client.post(
                        self.api_root_path + "/booking/notify",
                        json={
                            "telegram_id": telegram_id,
                            "time_start": booking.time_start.isoformat(),
                            "time_end": booking.time_end.isoformat(),
                            "booking_id": booking.id,
                        },
                        timeout=5,
                    )
                    status_code = response.status_code
                    response.raise_for_status()
                except httpx.TimeoutException:
                    logger.error(f"{base_log_message} is timed out")
                except httpx.HTTPStatusError:
                    logger.error(f"{base_log_message} failed with status code {status_code}")
                else:
                    logger.info(f"{base_log_message} completed succesfully")
                    break
                await asyncio.sleep(5)


tg_bot_client = TgBotClient(bot_settings.webhook_url)

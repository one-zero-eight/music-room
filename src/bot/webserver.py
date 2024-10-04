from src.bot.app import bot, configure_bot, dp
from src.config import bot_settings
from fastapi import FastAPI, Request, Response, status
from contextlib import asynccontextmanager
from aiogram.types import Update
from pydantic import BaseModel


class UserNotification(BaseModel):
    telegram_id: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    webhooh_url = f"{bot_settings.webhook_host}{bot_settings.webhook_secret}"
    await bot.set_webhook(url=webhooh_url)
    await configure_bot()
    yield
    await bot.delete_webhook()


app = FastAPI(lifespan=lifespan, root_path=f"/{bot_settings.webhook_secret}")


@app.post("")
async def webhook(request: Request) -> None:
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)


@app.post("/booking/notify")
async def notify_user_about_booking(user_data: UserNotification) -> Response:
    await bot.send_message(user_data.telegram_id, "Don't forget about your booking! It will start in an hour")
    return Response(status_code=status.HTTP_200_OK)

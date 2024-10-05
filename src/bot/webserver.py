from src.bot.app import bot
from src.config import bot_settings
from fastapi import FastAPI, Response, status
from pydantic import BaseModel


class UserNotification(BaseModel):
    telegram_id: int


app = FastAPI(root_path=f"/{bot_settings.webhook_secret}")


@app.post("/booking/notify")
async def notify_user_about_booking(user_data: UserNotification) -> Response:
    await bot.send_message(user_data.telegram_id, "Don't forget about your booking! It will start in an hour")
    return Response(status_code=status.HTTP_200_OK)

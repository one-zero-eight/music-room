from src.bot.app import bot
from src.config import bot_settings
from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from src.dependendies.auth import VerifiedDep
from src.schemas.auth import VerificationSource
from src.exceptions import ForbiddenException


class UserNotification(BaseModel):
    telegram_id: int


app = FastAPI(root_path=bot_settings.webhook_url)


@app.post("/booking/notify")
async def notify_user_about_booking(user_data: UserNotification, verification: VerifiedDep) -> Response:
    if verification.source != VerificationSource.BOT:
        raise ForbiddenException()
    await bot.send_message(user_data.telegram_id, "Don't forget about your booking! It will start in an hour")
    return Response(status_code=status.HTTP_200_OK)

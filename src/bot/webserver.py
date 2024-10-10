import datetime

from fastapi import FastAPI, Response, status
from pydantic import BaseModel

from src.bot.app import bot
from src.bot.logging_ import logger
from src.config import bot_settings
from src.dependendies.auth import VerifiedDep
from src.exceptions import ForbiddenException
from src.schemas.auth import VerificationSource


class BookingInfo(BaseModel):
    telegram_id: int
    booking_id: int
    time_start: datetime.datetime
    time_end: datetime.datetime


app = FastAPI(root_path=bot_settings.webhook_url)


@app.post("/booking/notify")
async def notify_user_about_booking(booking: BookingInfo, verification: VerifiedDep) -> Response:
    if verification.source != VerificationSource.BOT:
        raise ForbiddenException()
    seconds_till_booking = (booking.time_start - datetime.datetime.now()).seconds
    await bot.send_message(
        booking.telegram_id,
        f"Don't forget about your booking! It will start in {seconds_till_booking // 60} minutes. "
        "If you can't attend, please cancel the booking.\n"
        f"Your booking time: {booking.time_start.strftime("%H:%M")} - {booking.time_end.strftime("%H:%M")}.",
    )
    logger.info(f"Notification booking(id={booking.booking_id}), user(id={booking.telegram_id}) sent")
    return Response(status_code=status.HTTP_200_OK)

import datetime

from fastapi import FastAPI, Response, status
from pydantic import BaseModel

from src.bot.app import bot
from src.bot.logging_ import logger
from src.dependendies.auth import VerifiedDep
from src.exceptions import ForbiddenException
from src.schemas.auth import VerificationSource


class BookingInfo(BaseModel):
    telegram_id: int
    booking_id: int
    time_start: datetime.datetime
    time_end: datetime.datetime


app = FastAPI()


@app.post("/booking/notify")
async def notify_user_about_booking(booking: BookingInfo, verification: VerifiedDep) -> Response:
    if verification.source != VerificationSource.BOT:
        raise ForbiddenException()
    time_till_booking = booking.time_start - datetime.datetime.now()
    if time_till_booking > datetime.timedelta(seconds=0):
        seconds_till_booking = time_till_booking.seconds
        await bot.send_message(
            booking.telegram_id,
            f"Don't forget about your booking! It will start in {seconds_till_booking // 60} minutes. "
            "If you can't attend, please cancel the booking.\n"
            f"Your booking time: {booking.time_start.strftime("%H:%M")} - {booking.time_end.strftime("%H:%M")}.",
        )
        logger.info(f"Notification booking(id={booking.booking_id}), user(id={booking.telegram_id}) sent")
    else:
        logger.info(f"Notification booking(id={booking.booking_id}), user(id={booking.telegram_id}) is outdated")
    return Response(status_code=status.HTTP_200_OK)

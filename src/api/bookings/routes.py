__all__ = ["router"]

import datetime

from fastapi import APIRouter
from fastapi import Query, Response

from src.dependendies.auth import VerifiedDepWithUserID
from src.exceptions import (
    CollisionInBookings,
    NotEnoughDailyHoursToBook,
    NotEnoughWeeklyHoursToBook,
    NotWorkingHours,
    IncorrectOffset,
    ForbiddenException,
    NoSuchBooking,
)
from src.repositories.bookings.repository import booking_repository
from src.repositories.users.repository import user_repository
from src.schemas import CreateBooking, ViewBooking
from src.tools import count_duration, is_sc_working
from src.tools.utils import is_offset_correct


router = APIRouter(tags=["Bookings"])


def _get_start_of_week() -> datetime.date:
    _current_date = datetime.date.today()
    _start_of_week = _current_date - datetime.timedelta(days=_current_date.weekday())
    return _start_of_week


@router.post("/bookings/")
async def create_booking(booking: CreateBooking, verified: VerifiedDepWithUserID) -> ViewBooking | str:
    user_id = verified.user_id
    if not await is_sc_working(booking.time_start, booking.time_end):
        raise NotWorkingHours()

    collision = await booking_repository.check_collision(booking.time_start, booking.time_end)
    if collision is not None:
        raise CollisionInBookings()

    booking_duration = count_duration(booking.time_start, booking.time_end)

    if await user_repository.remaining_daily_hours(user_id, booking.time_start.date()) - booking_duration < 0:
        raise NotEnoughDailyHoursToBook()

    if await user_repository.remaining_weekly_hours(user_id, booking.time_start.date()) - booking_duration < 0:
        raise NotEnoughWeeklyHoursToBook()

    if not await is_offset_correct(booking.time_start):
        raise IncorrectOffset()

    created = await booking_repository.create(user_id, booking)
    return created


@router.delete("/bookings/{booking_id}")
async def delete_booking(booking_id: int, verified: VerifiedDepWithUserID) -> bool:
    booking = await booking_repository.get_booking(booking_id)

    if booking is None:
        raise NoSuchBooking()

    status = await user_repository.get_status(verified.user_id)

    if status != status.LORD and booking.user_id != verified.user_id:
        raise ForbiddenException()

    success = await booking_repository.delete_booking(booking_id)
    return success


@router.get("/bookings/my_bookings")
async def get_my_bookings(verified: VerifiedDepWithUserID) -> list[ViewBooking]:
    return await booking_repository.get_user_bookings(verified.user_id)


@router.get(
    "/bookings/form_schedule",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def form_schedule(
    start_of_week: datetime.date | None = Query(default_factory=_get_start_of_week, example=_get_start_of_week()),
) -> Response:
    image_bytes = await booking_repository.form_schedule(start_of_week)
    return Response(content=image_bytes, media_type="image/png")


@router.get("/bookings/daily_bookings")
async def daily_bookings(date: datetime.date) -> list[ViewBooking]:
    return await booking_repository.get_daily_bookings(date)

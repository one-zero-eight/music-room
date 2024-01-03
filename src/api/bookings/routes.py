import datetime
from typing import Optional

from fastapi import Query, Response

from src.api.bookings import router
from src.api.dependencies import Dependencies
from src.tools import count_duration, is_sc_working
from src.exceptions import (
    CollisionInBookings,
    IncompleteProfile,
    NotEnoughDailyHoursToBook,
    NotEnoughWeeklyHoursToBook,
    NotWorkingHours,
    IncorrectOffset,
)
from src.repositories.bookings.abc import AbstractBookingRepository
from src.repositories.participants.abc import AbstractParticipantRepository
from src.schemas import CreateBooking, ViewBooking
from src.tools.utils import is_offset_correct


def _get_start_of_week() -> datetime.date:
    _current_date = datetime.date.today()
    _start_of_week = _current_date - datetime.timedelta(days=_current_date.weekday())
    return _start_of_week


@router.post("/")
async def create_booking(
    booking: CreateBooking,
) -> ViewBooking | str:
    booking_repository = Dependencies.get(AbstractBookingRepository)
    participant_repository = Dependencies.get(AbstractParticipantRepository)

    if not await is_sc_working(booking.time_start, booking.time_end):
        raise NotWorkingHours()

    if await participant_repository.is_need_to_fill_profile(booking.participant_id):
        raise IncompleteProfile()

    collision = await booking_repository.check_collision(booking.time_start, booking.time_end)
    if collision is not None:
        raise CollisionInBookings()

    booking_duration = count_duration(booking.time_start, booking.time_end)

    if (
        await participant_repository.remaining_daily_hours(booking.participant_id, booking.time_start)
        - booking_duration
        < 0
    ):
        raise NotEnoughDailyHoursToBook()

    if await participant_repository.remaining_weekly_hours(booking.participant_id) - booking_duration < 0:
        raise NotEnoughWeeklyHoursToBook()

    if not await is_offset_correct(booking.time_start):
        raise IncorrectOffset()

    created = await booking_repository.create(booking)
    return created


@router.get("/")
async def get_bookings_for_week(
    start_of_week: Optional[datetime.date] = Query(default_factory=_get_start_of_week, example=_get_start_of_week()),
) -> list[ViewBooking]:
    booking_repository = Dependencies.get(AbstractBookingRepository)
    bookings = await booking_repository.get_bookings_for_week(start_of_week)
    return bookings


@router.delete("/{booking_id}/cancel_booking")
async def delete_booking(
    booking_id: int,
) -> bool:
    booking_repository = Dependencies.get(AbstractBookingRepository)
    success = await booking_repository.delete_booking(booking_id)
    return success


@router.get("/form_schedule", responses={200: {"content": {"image/png": {}}}}, response_class=Response)
async def form_schedule(
    start_of_week: Optional[datetime.date] = Query(default_factory=_get_start_of_week, example=_get_start_of_week()),
) -> Response:
    booking_repository = Dependencies.get(AbstractBookingRepository)
    image_bytes = await booking_repository.form_schedule(start_of_week)
    return Response(content=image_bytes, media_type="image/png")


@router.get("/daily_bookings")
async def daily_bookings(date: datetime.date) -> list[ViewBooking]:
    booking_repository = Dependencies.get(AbstractBookingRepository)
    return await booking_repository.get_daily_bookings(date)


@router.get("/{participant_id}")
async def participant_bookings(participant_id: int) -> list[ViewBooking]:
    booking_repository = Dependencies.get(AbstractBookingRepository)
    return await booking_repository.get_participant_bookings(participant_id)

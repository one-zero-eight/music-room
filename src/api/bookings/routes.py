import datetime
from typing import Optional

from fastapi import Query, Response

from src.api.bookings import router
from src.api.dependencies import Dependencies, VerifiedDep
from src.tools import count_duration, is_sc_working
from src.exceptions import (
    CollisionInBookings,
    IncompleteProfile,
    NotEnoughDailyHoursToBook,
    NotEnoughWeeklyHoursToBook,
    NotWorkingHours,
    IncorrectOffset,
    ForbiddenException,
    NoSuchBooking,
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
    booking: CreateBooking, verified: VerifiedDep
) -> ViewBooking | str:
    booking_repository = Dependencies.get(AbstractBookingRepository)
    participant_repository = Dependencies.get(AbstractParticipantRepository)
    user_id = verified.user_id
    if not await is_sc_working(booking.time_start, booking.time_end):
        raise NotWorkingHours()

    if await participant_repository.is_need_to_fill_profile(user_id):
        raise IncompleteProfile()

    collision = await booking_repository.check_collision(
        booking.time_start, booking.time_end
    )
    if collision is not None:
        raise CollisionInBookings()

    booking_duration = count_duration(booking.time_start, booking.time_end)

    if (
        await participant_repository.remaining_daily_hours(user_id, booking.time_start)
        - booking_duration
        < 0
    ):
        raise NotEnoughDailyHoursToBook()

    if (
        await participant_repository.remaining_weekly_hours(user_id) - booking_duration
        < 0
    ):
        raise NotEnoughWeeklyHoursToBook()

    if not await is_offset_correct(booking.time_start):
        raise IncorrectOffset()

    created = await booking_repository.create(user_id, booking)
    return created


@router.delete("/{booking_id}")
async def delete_booking(
    booking_id: int,
    verified: VerifiedDep,
) -> bool:
    booking_repository = Dependencies.get(AbstractBookingRepository)
    booking = await booking_repository.get_booking(booking_id)

    if booking is None:
        raise NoSuchBooking()

    if booking.participant_id != verified.user_id:
        raise ForbiddenException()

    success = await booking_repository.delete_booking(booking_id)
    return success


@router.get("/my_bookings")
async def get_my_bookings(verified: VerifiedDep) -> list[ViewBooking]:
    booking_repository = Dependencies.get(AbstractBookingRepository)
    return await booking_repository.get_participant_bookings(verified.user_id)


@router.get(
    "/form_schedule",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def form_schedule(
    start_of_week: Optional[datetime.date] = Query(
        default_factory=_get_start_of_week, example=_get_start_of_week()
    ),
) -> Response:
    booking_repository = Dependencies.get(AbstractBookingRepository)
    image_bytes = await booking_repository.form_schedule(start_of_week)
    return Response(content=image_bytes, media_type="image/png")


@router.get("/daily_bookings")
async def daily_bookings(date: datetime.date) -> list[ViewBooking]:
    booking_repository = Dependencies.get(AbstractBookingRepository)
    return await booking_repository.get_daily_bookings(date)


@router.get("/")
async def get_bookings_for_week(
    start_of_week: Optional[datetime.date] = Query(
        default_factory=_get_start_of_week, example=_get_start_of_week()
    ),
) -> list[ViewBooking]:
    booking_repository = Dependencies.get(AbstractBookingRepository)
    bookings = await booking_repository.get_bookings_for_week(start_of_week)
    return bookings

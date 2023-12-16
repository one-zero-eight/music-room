from src.api.bookings import router
from src.api.dependencies import Dependencies
from src.tools import count_duration, is_sc_working
from src.exceptions import (
    CollisionInBookings,
    IncompleteProfile,
    NotEnoughDailyHoursToBook,
    NotEnoughWeeklyHoursToBook,
    NotWorkingHours,
)
from src.repositories.bookings.abc import AbstractBookingRepository
from src.repositories.participants.abc import AbstractParticipantRepository
from src.schemas import CreateBooking, ViewBooking


@router.post("/create_booking")
async def create_booking(
    booking: "CreateBooking",
) -> ViewBooking | str:
    booking_repository = Dependencies.f(AbstractBookingRepository)
    participant_repository = Dependencies.f(AbstractParticipantRepository)

    if not await is_sc_working(booking.time_start, booking.time_end):
        raise NotWorkingHours()
    else:
        if await participant_repository.is_need_to_fill_profile(booking.participant_id):
            raise IncompleteProfile()
        else:
            if not await booking_repository.check_collision(booking.time_start, booking.time_end):
                booking_duration = await count_duration(booking.time_start, booking.time_end)

                if (
                    await participant_repository.remaining_daily_hours(booking.participant_id, booking.time_start)
                    - booking_duration
                    < 0
                ):
                    raise NotEnoughDailyHoursToBook()

                elif await participant_repository.remaining_weekly_hours(booking.participant_id) - booking_duration < 0:
                    raise NotEnoughWeeklyHoursToBook()
                else:
                    created = await booking_repository.create(booking)
                    return created
            else:
                raise CollisionInBookings()


@router.get("")
async def get_bookings_for_current_week(current_week: bool) -> list[ViewBooking]:
    booking_repository = Dependencies.f(AbstractBookingRepository)
    bookings = await booking_repository.get_bookings_for_current_week(current_week)
    return bookings


@router.delete("/{booking_id}/cancel_booking")
async def delete_booking(
    booking_id: int,
) -> ViewBooking:
    booking_repository = Dependencies.f(AbstractBookingRepository)
    return await booking_repository.delete_booking(booking_id)


@router.get("/form_schedule")
async def form_schedule(current_week: bool) -> str:
    booking_repository = Dependencies.f(AbstractBookingRepository)
    return await booking_repository.form_schedule(current_week)

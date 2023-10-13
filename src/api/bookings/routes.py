from starlette.responses import JSONResponse

from src.api.bookings import router
from src.api.dependencies import (BOOKING_REPOSITORY_DEPENDENCY,
                                  PARTICIPANT_REPOSITORY_DEPENDENCY)
from src.api.exceptions import (CollisionInBooking, IncompleteProfile,
                                NotEnoughDailyHoursToBook,
                                NotEnoughWeeklyHoursToBook, NotWorkingHours)
from src.api.tools.utils import count_duration, is_sc_working
from src.schemas import CreateBooking, ViewBooking


@router.post("/create_booking")
async def create_booking(
        booking: "CreateBooking",
        booking_repository: BOOKING_REPOSITORY_DEPENDENCY,
        participant_repository: PARTICIPANT_REPOSITORY_DEPENDENCY,
) -> ViewBooking | str:
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
                raise CollisionInBooking()


@router.get("")
async def get_bookings_for_current_week(
        booking_repository: BOOKING_REPOSITORY_DEPENDENCY,
) -> list[ViewBooking]:
    bookings = await booking_repository.get_bookings_for_current_week()
    return bookings


@router.delete("/{booking_id}/cancel_booking")
async def delete_booking(
        booking_id: int,
        booking_repository: BOOKING_REPOSITORY_DEPENDENCY,
) -> ViewBooking:
    return await booking_repository.delete_booking(booking_id)


@router.get("/form_schedule")
async def form_schedule(booking_repository: BOOKING_REPOSITORY_DEPENDENCY):
    return await booking_repository.form_schedule()

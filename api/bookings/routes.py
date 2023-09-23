from api.bookings import router
from api.dependencies import BOOKING_REPOSITORY_DEPENDENCY
from schemas import CreateBooking, ViewBooking


@router.post("/create_booking")
async def create_booking(
    booking: "CreateBooking",
    booking_repository: BOOKING_REPOSITORY_DEPENDENCY,
) -> ViewBooking:
    created = await booking_repository.create(booking)
    return created


@router.get("/bookings")
async def get_bookings_for_current_week(
    booking_repository: BOOKING_REPOSITORY_DEPENDENCY,
) -> list[ViewBooking]:
    bookings = await booking_repository.get_bookings_for_current_week()
    return bookings


@router.delete("/{booking_id}/cancel_booking/")
async def delete_booking(
    booking_id: int,
    booking_repository: BOOKING_REPOSITORY_DEPENDENCY,
) -> None:
    await booking_repository.delete_booking(booking_id)

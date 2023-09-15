from api.bookings import router
from api.dependencies import BOOKING_REPOSITORY_DEPENDENCY
from schemas import CreateBooking, ViewBooking


@router.post("/", response_model=None)
async def create_booking(
    booking: CreateBooking,
    booking_repository: BOOKING_REPOSITORY_DEPENDENCY,
) -> ViewBooking:
    created = await booking_repository.create(booking)
    return created

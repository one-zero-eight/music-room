import datetime
from abc import ABCMeta, abstractmethod

from schemas import CreateBooking, ViewBooking


class AbstractBookingRepository(metaclass=ABCMeta):
    # ------------------- CRUD ------------------- #
    @abstractmethod
    async def create(self, event: "CreateBooking") -> "ViewBooking":
        ...

    @abstractmethod
    async def get_bookings_for_current_week(self):
        ...

    @abstractmethod
    async def delete_booking(self, booking_id) -> ViewBooking:
        ...

    @abstractmethod
    async def check_collision(self, time_start: datetime.datetime, time_end: datetime.datetime) -> bool:
        ...

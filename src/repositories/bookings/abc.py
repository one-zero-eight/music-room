import datetime
from abc import ABCMeta, abstractmethod
from typing import Optional

from src.schemas import CreateBooking, ViewBooking, ViewParticipant


class AbstractBookingRepository(metaclass=ABCMeta):
    # ------------------- CRUD ------------------- #
    @abstractmethod
    async def create(
        self, participant_id: int, booking: "CreateBooking"
    ) -> "ViewBooking":
        ...

    @abstractmethod
    async def get_bookings_for_week(self, start_of_week: datetime.date):
        ...

    @abstractmethod
    async def get_booking(self, booking_id: int) -> Optional["ViewBooking"]:
        ...

    @abstractmethod
    async def delete_booking(self, booking_id) -> bool:
        ...

    @abstractmethod
    async def check_collision(
        self, time_start: datetime.datetime, time_end: datetime.datetime
    ) -> Optional[ViewBooking]:
        ...

    @abstractmethod
    async def get_participant(self, participant_id) -> ViewParticipant:
        ...

    @abstractmethod
    async def form_schedule(self, start_of_week: datetime.date) -> bytes:
        ...

    @abstractmethod
    async def get_daily_bookings(self, date: datetime.date) -> list[ViewBooking]:
        ...

    @abstractmethod
    async def get_participant_bookings(self, participant_id: int) -> list[ViewBooking]:
        ...

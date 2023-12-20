import datetime
from abc import ABCMeta, abstractmethod

from src.schemas import CreateBooking, ViewBooking, ViewParticipantBeforeBooking


class AbstractBookingRepository(metaclass=ABCMeta):
    # ------------------- CRUD ------------------- #
    @abstractmethod
    async def create(self, event: "CreateBooking") -> "ViewBooking":
        ...

    @abstractmethod
    async def get_bookings_for_current_week(self, current_week: bool):
        ...

    @abstractmethod
    async def delete_booking(self, booking_id) -> bool:
        ...

    @abstractmethod
    async def check_collision(self, time_start: datetime.datetime, time_end: datetime.datetime) -> bool:
        ...

    @abstractmethod
    async def get_participant(self, participant_id) -> ViewParticipantBeforeBooking:
        ...

    @abstractmethod
    async def form_schedule(self, current_week: bool) -> str:
        ...

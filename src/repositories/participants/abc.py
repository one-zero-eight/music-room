import datetime
from abc import ABCMeta, abstractmethod
from typing import Optional

from src.schemas import CreateParticipant, FillParticipantProfile, ViewBooking, ViewParticipantBeforeBooking


class AbstractParticipantRepository(metaclass=ABCMeta):
    @abstractmethod
    async def create(self, participant: "CreateParticipant") -> "ViewParticipantBeforeBooking":
        ...

    @abstractmethod
    async def fill_profile(self, participant: "FillParticipantProfile") -> "ViewParticipantBeforeBooking":
        ...

    @abstractmethod
    async def change_status(self, participant_id: int, new_status: str) -> "ViewParticipantBeforeBooking":
        ...

    @abstractmethod
    async def get_participant_bookings(self, participant_id: int) -> list["ViewBooking"]:
        ...

    @abstractmethod
    async def get_status(self, participant_id: int) -> str:
        ...

    @abstractmethod
    async def remaining_weekly_hours(self, participant_id: int, start_of_week: Optional[datetime.date] = None) -> float:
        ...

    @abstractmethod
    async def remaining_daily_hours(self, participant_id: int, date: datetime.date) -> float:
        ...

    @abstractmethod
    async def is_need_to_fill_profile(self, participant_id: int) -> bool:
        ...

    @abstractmethod
    async def get_phone_number(self, participant_id: int):
        ...

    @abstractmethod
    async def get_participant_id(self, telegram_id: str) -> int:
        ...

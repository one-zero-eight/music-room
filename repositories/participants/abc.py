from abc import ABCMeta, abstractmethod

from schemas import CreateParticipant, ViewParticipantBeforeBooking


class AbstractParticipantRepository(metaclass=ABCMeta):
    # ------------------- CRUD ------------------- #
    @abstractmethod
    async def create(
        self, event: "CreateParticipant"
    ) -> "ViewParticipantBeforeBooking":
        ...

    @abstractmethod
    async def change_status(
        self, participant_id: "ViewParticipantBeforeBooking", new_status: str
    ) -> "ViewParticipantBeforeBooking":
        ...

    @abstractmethod
    async def change_daily_hours(
        self, participant_id: "ViewParticipantBeforeBooking", new_hours: int
    ) -> "ViewParticipantBeforeBooking":
        ...

    @abstractmethod
    async def change_weekly_hours(
        self, participant_id: "ViewParticipantBeforeBooking", new_hours: int
    ) -> "ViewParticipantBeforeBooking":
        ...

    @abstractmethod
    async def get_participant_bookings(
        self, participant_id: int
    ) -> list["ViewBooking"]:
        ...

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from api.tools.tools import count_duration, max_hours_to_book_per_week
from repositories.participants.abc import AbstractParticipantRepository
from schemas import CreateParticipant, ViewBooking, ViewParticipantBeforeBooking
from storage.sql import AbstractSQLAlchemyStorage
from storage.sql.models import Booking, Participant


class SqlParticipantRepository(AbstractParticipantRepository):
    storage: AbstractSQLAlchemyStorage

    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    async def create(self, participant: "CreateParticipant") -> "ViewParticipantBeforeBooking":
        async with self._create_session() as session:
            query = (
                insert(Participant)
                .values(**participant.model_dump())
                .returning(Participant)
            )
            obj = await session.scalar(query)
            await session.commit()
            return ViewParticipantBeforeBooking.model_validate(obj)

    async def change_status(self, participant_id: int, new_status: str) -> "ViewParticipantBeforeBooking":
        async with self._create_session() as session:
            query = (
                update(Participant)
                .where(Participant.id == participant_id)
                .values(status=new_status)
                .returning(Participant)
            )
            obj = await session.scalar(query)
            await session.commit()
            return ViewParticipantBeforeBooking.model_validate(obj)

    async def get_participant_bookings(self, participant_id: int) -> list["ViewBooking"]:
        async with self._create_session() as session:
            query = select(Booking).where(Booking.participant_id == participant_id)
            objs = await session.scalars(query)
            if objs:
                return [ViewBooking.model_validate(obj) for obj in objs]

    async def get_status(self, participant_id: int) -> str:
        async with self._create_session() as session:
            query = select(Participant).where(Participant.id == participant_id)
            obj = await session.scalar(query)
            return obj.status

    async def get_estimated_weekly_hours(self, participant_id: int) -> float:
        async with self._create_session() as session:
            query1 = select(Booking).where(Booking.participant_id == participant_id)
            objs = await session.scalars(query1)
            spent_hours = 0
            for obj in objs:
                spent_hours += float(count_duration(obj.time_start, obj.time_end))
            return max_hours_to_book_per_week(await self.get_status(participant_id)) - spent_hours

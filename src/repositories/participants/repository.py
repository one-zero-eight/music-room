import datetime
from datetime import timedelta
from typing import Optional

from sqlalchemy import and_, between, extract, select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.participants.abc import AbstractParticipantRepository
from src.schemas import CreateParticipant, FillParticipantProfile, ViewBooking, ViewParticipantBeforeBooking
from src.storage.sql import AbstractSQLAlchemyStorage
from src.storage.sql.models import Booking, Participant
from src.tools import Crypto
from src.tools import count_duration, max_hours_to_book_per_day, max_hours_to_book_per_week


class SqlParticipantRepository(AbstractParticipantRepository):
    storage: AbstractSQLAlchemyStorage

    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    async def create(self, participant: "CreateParticipant") -> "ViewParticipantBeforeBooking":
        async with self._create_session() as session:
            query = insert(Participant).values(**participant.model_dump()).returning(Participant)
            obj = await session.scalar(query)
            await session.commit()
            return ViewParticipantBeforeBooking.model_validate(obj)

    async def fill_profile(self, participant: "FillParticipantProfile") -> "ViewParticipantBeforeBooking":
        async with self._create_session() as session:
            phone_number = Crypto.encrypt(participant.phone_number)
            query = (
                update(Participant)
                .where(Participant.email == participant.email)
                .values(
                    name=participant.name,
                    alias=participant.alias,
                    email=participant.email,
                    phone_number=phone_number,
                    need_to_fill_profile=False,
                )
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
            if obj is not None:
                return obj.status

    async def remaining_weekly_hours(self, participant_id: int, start_of_week: Optional[datetime.date] = None) -> float:
        async with self._create_session() as session:
            if start_of_week is None:
                today = datetime.date.today()
                start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            query = select(Booking).filter(
                Booking.participant_id == participant_id, between(Booking.time_start, start_of_week, end_of_week)
            )
            objs = await session.scalars(query)
            spent_hours = 0
            for obj in objs:
                spent_hours += float(count_duration(obj.time_start, obj.time_end))
            return max_hours_to_book_per_week(await self.get_status(participant_id)) - spent_hours

    async def remaining_daily_hours(self, participant_id: int, date: datetime.date) -> float:
        async with self._create_session() as session:
            query = select(Booking).where(
                and_(
                    Booking.participant_id == participant_id,
                    extract("day", Booking.time_start) == date.day,
                    extract("year", Booking.time_start) == date.year,
                    extract("month", Booking.time_start) == date.month,
                )
            )
            objs = await session.scalars(query)
            spent_hours = 0
            for obj in objs:
                spent_hours += float(count_duration(obj.time_start, obj.time_end))
            return max_hours_to_book_per_day(await self.get_status(participant_id)) - spent_hours

    async def is_need_to_fill_profile(self, participant_id: int) -> bool:
        async with self._create_session() as session:
            query = select(Participant).where(
                and_(Participant.id == participant_id, Participant.need_to_fill_profile is True)
            )
            obj = await session.scalar(query)
            if obj:
                return True
            return False

    async def get_phone_number(self, participant_id: int):
        async with self._create_session() as session:
            query = select(Participant).where(Participant.id == participant_id)
            obj = await session.scalar(query)
            return Crypto.decrypt(obj.phone_number)

    async def get_participant_id(self, telegram_id: str) -> int:
        async with self._create_session() as session:
            query = select(Participant).where(Participant.telegram_id == telegram_id)
            obj = await session.scalar(query)
            return obj.id

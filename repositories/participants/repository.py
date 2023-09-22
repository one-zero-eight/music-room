from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from api.tools.validation import (max_hours_to_book_per_day,
                                  max_hours_to_book_per_week)
from repositories.participants.abc import AbstractParticipantRepository
from schemas import CreateParticipant, ViewParticipantBeforeBooking
from storage.sql import AbstractSQLAlchemyStorage
from storage.sql.models import Participant


class SqlParticipantRepository(AbstractParticipantRepository):
    storage: AbstractSQLAlchemyStorage

    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    # ----------------- CRUD ----------------- #

    async def create(
            self, participant: "CreateParticipant"
    ) -> "ViewParticipantBeforeBooking":
        async with self._create_session() as session:
            query = (
                insert(Participant)
                .values(
                    daily_hours=max_hours_to_book_per_day(participant.status),
                    weekly_hours=max_hours_to_book_per_week(participant.status),
                    **participant.model_dump()
                )
                .returning(Participant)
            )
            obj = await session.scalar(query)
            await session.commit()
            return ViewParticipantBeforeBooking.model_validate(obj)

    async def change_status(
            self, participant_id: "ViewParticipantBeforeBooking", new_status: str
    ) -> "ViewParticipantBeforeBooking":
        async with self._create_session() as session:
            query = (
                update(Participant)
                .where(Participant.id == participant_id)
                .values(
                    status=new_status,
                    daily_hours=max_hours_to_book_per_day(new_status),
                    weekly_hours=max_hours_to_book_per_week(new_status),
                )
                .returning(Participant)
            )
            obj = await session.scalar(query)
            await session.commit()
            return ViewParticipantBeforeBooking.model_validate(obj)

    async def change_daily_hours(
            self, participant_id: "ViewParticipantBeforeBooking", new_hours: int
    ) -> "ViewParticipantBeforeBooking":
        async with self._create_session() as session:
            query = (
                update(Participant)
                .where(Participant.id == participant_id)
                .values(daily_hours=new_hours)
                .returning(Participant)
            )
            obj = await session.scalar(query)
            await session.commit()
            return ViewParticipantBeforeBooking.model_validate(obj)

    async def change_weekly_hours(
            self, participant_id: "ViewParticipantBeforeBooking", new_hours: int
    ) -> "ViewParticipantBeforeBooking":
        async with self._create_session() as session:
            query = (
                update(Participant)
                .where(Participant.id == participant_id)
                .values(weekly_hours=new_hours)
                .returning(Participant)
            )
            obj = await session.scalar(query)
            await session.commit()
            return ViewParticipantBeforeBooking.model_validate(obj)

import datetime
from datetime import date, timedelta

from sqlalchemy import and_, between, delete, extract, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from api.tools.utils import count_duration
from repositories.bookings.abc import AbstractBookingRepository
from schemas import CreateBooking, ViewBooking
from storage.sql import AbstractSQLAlchemyStorage
from storage.sql.models import Booking


class SqlBookingRepository(AbstractBookingRepository):
    storage: AbstractSQLAlchemyStorage

    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    async def create(self, booking: "CreateBooking") -> "ViewBooking":
        async with self._create_session() as session:
            query = insert(Booking).values(**booking.model_dump()).returning(Booking)
            obj = await session.scalar(query)
            await session.commit()
            return ViewBooking.model_validate(obj)

    async def get_bookings_for_current_week(self) -> list["ViewBooking"]:
        async with self._create_session() as session:
            today = date.today()
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)

            query = select(Booking).filter(between(Booking.time_start, start_of_week, end_of_week))

            objs = await session.scalars(query)
            if objs:
                return [ViewBooking.model_validate(obj) for obj in objs]

    async def delete_booking(self, booking_id) -> ViewBooking:
        async with self._create_session() as session:
            query = delete(Booking).where(Booking.id == booking_id).returning(Booking)
            obj = await session.scalar(query)
            await session.commit()
            return ViewBooking.model_validate(obj)

    async def check_collision(self, time_start: datetime.datetime, time_end: datetime.datetime) -> bool:
        async with self._create_session() as session:
            query = select(Booking).where(and_(Booking.time_start < time_end, Booking.time_end > time_start))
            collision_exists = await session.scalar(query)
            return collision_exists is not None

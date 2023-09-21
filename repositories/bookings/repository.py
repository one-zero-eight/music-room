from datetime import date, timedelta

from sqlalchemy import and_, extract, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

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

    # ----------------- CRUD ----------------- #

    async def create(self, booking: "CreateBooking") -> "ViewBooking":
        async with self._create_session() as session:
            query = insert(Booking).values(**booking.model_dump()).returning(Booking)
            obj = await session.scalar(query)
            await session.commit()
            return ViewBooking.model_validate(obj)

    async def get_bookings_for_current_week(self) -> list["ViewBooking"]:
        async with self._create_session() as session:
            today = date.today()
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
            query = select(Booking).where(
                and_(
                    extract("day", Booking.time_start) >= int(str(start)[-2:]),
                    extract("year", Booking.time_start) == int(str(start)[:4]),
                    extract("day", Booking.time_end) <= int(str(end)[-2:]),
                    extract("month", Booking.time_start) == int(str(start)[5:7]),
                    extract("month", Booking.time_end) == int(str(end)[5:7]),
                )
            )
            objs = await session.scalars(query)
            if objs:
                return [ViewBooking.model_validate(obj) for obj in objs]

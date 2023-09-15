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

__all__ = ["user_repository", "SqlUserRepository"]

import datetime
from datetime import timedelta
from typing import Self

from sqlalchemy import and_, between, extract, select, update, insert, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import CreateUser, FillUserProfile, ViewBooking, ViewUser
from src.schemas.user import UserStatus
from src.storage.sql import AbstractSQLAlchemyStorage
from src.storage.sql.models import Booking, User
from src.tools import count_duration


class SqlUserRepository:
    storage: AbstractSQLAlchemyStorage

    def update_storage(self, storage: AbstractSQLAlchemyStorage) -> Self:
        self.storage = storage
        return self

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    async def create(self, user: CreateUser) -> ViewUser:
        async with self._create_session() as session:
            query = insert(User).values(**user.model_dump()).returning(User)
            obj = await session.scalar(query)
            await session.commit()
            return ViewUser.model_validate(obj)

    async def get_user(self, user_id: int) -> ViewUser | None:
        async with self._create_session() as session:
            query = select(User).where(User.id == user_id)
            obj = await session.scalar(query)
            if obj:
                return ViewUser.model_validate(obj)

    async def get_multiple_users(self, user_ids: list[int]) -> list[ViewUser | None]:
        async with self._create_session() as session:
            query = select(User).where(User.id.in_(user_ids))
            objs = await session.scalars(query)
            return [ViewUser.model_validate(obj) for obj in objs]

    async def get_all_users(self) -> list[ViewUser]:
        async with self._create_session() as session:
            query = select(User)
            objs = await session.scalars(query)
            return [ViewUser.model_validate(obj) for obj in objs]

    async def fill_profile(self, user_id: int, data: "FillUserProfile") -> ViewUser:
        async with self._create_session() as session:
            query = update(User).where(User.id == user_id).values(name=data.name, alias=data.alias).returning(User)
            obj = await session.scalar(query)
            await session.commit()
            return ViewUser.model_validate(obj)

    async def get_user_bookings(self, user_id: int) -> list["ViewBooking"]:
        async with self._create_session() as session:
            query = select(Booking).where(Booking.user_id == user_id)
            objs = await session.scalars(query)
            if objs:
                return [ViewBooking.model_validate(obj) for obj in objs]

    async def get_status(self, user_id: int) -> UserStatus:
        async with self._create_session() as session:
            query = select(User.status).where(User.id == user_id)
            status = await session.scalar(query)
            if status is None:
                return UserStatus.FREE
            return UserStatus(status)

    async def remaining_weekly_hours(self, user_id: int, start_of_week: datetime.date | None = None) -> float:
        async with self._create_session() as session:
            if start_of_week is None:
                today = datetime.date.today()
                start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            query = select(Booking).filter(
                Booking.user_id == user_id,
                between(Booking.time_start, start_of_week, end_of_week),
            )
            objs = await session.scalars(query)
            spent_hours = 0
            for obj in objs:
                spent_hours += float(count_duration(obj.time_start, obj.time_end))
            status = await self.get_status(user_id)
            return status.max_hours_to_book_per_week() - spent_hours

    async def remaining_daily_hours(self, user_id: int, date: datetime.date) -> float:
        async with self._create_session() as session:
            query = select(Booking).where(
                and_(
                    Booking.user_id == user_id,
                    extract("day", Booking.time_start) == date.day,
                    extract("year", Booking.time_start) == date.year,
                    extract("month", Booking.time_start) == date.month,
                )
            )
            objs = await session.scalars(query)
            spent_hours = 0
            for obj in objs:
                spent_hours += float(count_duration(obj.time_start, obj.time_end))
            status = await self.get_status(user_id)
            return status.max_hours_to_book_per_day() - spent_hours

    async def get_user_id(self, telegram_id: int | None = None, email: str | None = None) -> int | None:
        async with self._create_session() as session:
            if telegram_id is None and email is None:
                return None
            clauses = []
            if email is not None:
                clauses.append(User.email == email)
            if telegram_id is not None:
                clauses.append(User.telegram_id == telegram_id)
            query = select(User.id).where(or_(*clauses))
            user_id = await session.scalar(query)
            return user_id


user_repository: SqlUserRepository = SqlUserRepository()

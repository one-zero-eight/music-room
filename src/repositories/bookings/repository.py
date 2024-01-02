import datetime
import io
from datetime import timedelta
from datetime import datetime as datetime_datetime
from typing import Optional

from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import and_, between, select, insert, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import NoSuchBooking
from src.repositories.bookings.abc import AbstractBookingRepository
from src.schemas import CreateBooking, ViewBooking, ViewParticipant, HelpBooking
from src.storage.sql import AbstractSQLAlchemyStorage
from src.storage.sql.models import Booking, Participant
from src.tools import count_duration


class SqlBookingRepository(AbstractBookingRepository):
    storage: AbstractSQLAlchemyStorage

    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    async def create(self, booking: "CreateBooking") -> ViewBooking:
        async with self._create_session() as session:
            query = insert(Booking).values(**booking.model_dump()).returning(Booking)
            obj = await session.scalar(query)
            await session.commit()
            await session.refresh(obj)
            return ViewBooking.model_validate(obj)

    async def get_bookings_for_week(self, start_of_week: datetime.date) -> list[ViewBooking]:
        async with self._create_session() as session:
            end_of_week = start_of_week + timedelta(days=7)
            query = select(Booking).filter(between(Booking.time_start, start_of_week, end_of_week))

            objs = await session.scalars(query)
            if objs:
                return [ViewBooking.model_validate(obj) for obj in objs]

    async def delete_booking(self, booking_id) -> bool:
        async with self._create_session() as session:
            query = delete(Booking).where(Booking.id == booking_id).returning(Booking)
            obj = await session.scalar(query)
            await session.commit()
            if obj:
                return True
            raise NoSuchBooking()

    async def check_collision(
        self, time_start: datetime.datetime, time_end: datetime.datetime
    ) -> Optional[ViewBooking]:
        async with self._create_session() as session:
            query = select(Booking).where(
                or_(
                    between(Booking.time_start, time_start, time_end),
                    between(Booking.time_end, time_start, time_end),
                )
            )
            collision = await session.scalar(query)
            return collision

    async def get_participant(self, participant_id) -> ViewParticipant:
        async with self._create_session() as session:
            query = select(Participant).where(Participant.id == participant_id)
            obj = await session.scalar(query)
            return ViewParticipant.model_validate(obj)

    async def form_schedule(self, start_of_week: datetime.date) -> bytes:
        xbase = 48  # origin for x
        ybase = 73  # origin for y
        xsize = 175.5  # length of the rect by x-axis
        ysize = 32  # length of the rect by x-axis

        # Create a new image using PIL
        image = Image.open("src/repositories/bookings/schedule.jpg")
        draw = ImageDraw.Draw(image)

        lightGray = (211, 211, 211)
        lightBlack = (48, 54, 59)
        red = (255, 0, 0)

        fontSimple = ImageFont.truetype("src/repositories/bookings/open_sans.ttf", size=14)

        bookings = await self.get_bookings_for_week(start_of_week)
        for booking in bookings:
            day = booking.time_start.weekday()

            ylength = count_duration(booking.time_start, booking.time_end)
            x0 = xbase + xsize * day
            y0 = ybase + int(ysize * ((booking.time_start.hour - 7) + (booking.time_start.minute / 60.0)))
            x1 = x0 + xsize
            y1 = y0 + 31.5 * ylength

            draw.rounded_rectangle((x0, y0, x1, y1), 2, fill=lightGray)
            participant = await self.get_participant(booking.participant_id)

            alias = participant.alias
            if len(alias) > 11:
                alias = f"{alias[:11]}..."

            caption = f"{alias} "

            # noinspection SqlAlchemyUnsafeQuery
            draw.text(
                (x0 + 2, (y0 + y1) / 2 - 9),
                text=f"{caption}{booking.time_start.strftime('%H:%M')}-{booking.time_end.strftime('%H:%M')}",
                fill=lightBlack,
                font=fontSimple,
            )

        today = datetime.date.today()
        weekday = today.weekday()

        current = datetime.datetime.now()
        is_current_week = False
        if start_of_week <= current.date() <= start_of_week + timedelta(days=6):
            is_current_week = True

        if 6 < current.hour < 23 and is_current_week:
            now_x0 = xbase + xsize * weekday
            now_y0 = ybase + int(ysize * ((current.hour - 7) + (current.minute / 60)))
            draw.rounded_rectangle((now_x0, now_y0, now_x0 + xsize, now_y0 + 2), 2, fill=red)

        image_stream = io.BytesIO()
        image.save(image_stream, format="png")
        val = image_stream.getvalue()
        image_stream.close()
        return val

    async def get_daily_bookings(self, date: datetime.date) -> list[HelpBooking]:
        async with self._create_session() as session:
            start_of_day = datetime_datetime.combine(date, datetime.time.min)
            end_of_day = datetime_datetime.combine(date, datetime.time.max)

            query = select(Booking).where(and_(Booking.time_start >= start_of_day, Booking.time_end <= end_of_day))

            objs = await session.scalars(query)

            return [HelpBooking.model_validate(obj) for obj in objs]

    async def get_participant_bookings(self, participant_id: int) -> list[HelpBooking]:
        async with self._create_session() as session:
            query = select(Booking).where(Booking.participant_id == participant_id)
            objs = await session.scalars(query)
            return [HelpBooking.model_validate(obj) for obj in objs]

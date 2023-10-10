import datetime
import io
from datetime import date, timedelta

from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import and_, between, delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from api.tools.utils import count_duration
from repositories.bookings.abc import AbstractBookingRepository
from schemas import CreateBooking, ViewBooking, ViewParticipantBeforeBooking
from storage.sql import AbstractSQLAlchemyStorage
from storage.sql.models import Booking, Participant


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
            return ViewBooking.model_validate(obj)

    async def get_bookings_for_current_week(self) -> list[ViewBooking]:
        async with (self._create_session() as session):
            current_datetime = datetime.datetime.now()
            next_week_delta = 0

            if current_datetime.weekday() == 6 and current_datetime.hour >= 22 and current_datetime.minute > 30:
                next_week_delta = 8

            today = date.today()
            start_of_week = (today - timedelta(days=today.weekday() + 1)) + timedelta(days=next_week_delta)
            end_of_week = start_of_week + timedelta(days=6)

            query = select(Booking).filter(between(Booking.time_start, start_of_week, end_of_week))

            objs = await session.scalars(query)
            if objs:
                return [ViewBooking.model_validate(obj) for obj in objs]

    async def delete_booking(self, booking_id) -> ViewBooking | dict[str, str]:
        async with self._create_session() as session:
            query = delete(Booking).where(Booking.id == booking_id).returning(Booking)
            obj = await session.scalar(query)
            await session.commit()
            if obj:
                return ViewBooking.model_validate(obj)
            return {"message": "No such booking"}

    async def check_collision(self, time_start: datetime.datetime, time_end: datetime.datetime) -> bool:
        async with self._create_session() as session:
            query = select(Booking).where(and_(Booking.time_start < time_end, Booking.time_end > time_start))
            collision_exists = await session.scalar(query)
            return collision_exists is not None

    async def get_participant(self, participant_id) -> ViewParticipantBeforeBooking:
        async with self._create_session() as session:
            query = select(Participant).where(Participant.id == participant_id)
            obj = await session.scalar(query)
            return ViewParticipantBeforeBooking.model_validate(obj)

    async def form_schedule(self):
        xbase = 48  # origin for x
        ybase = 73  # origin for y
        xsize = 175.5  # length of the rect by x-axis
        ysize = 32  # length of the rect by x-axis

        # Create a new image using PIL
        image = Image.open("repositories/bookings/schedule.jpg")
        draw = ImageDraw.Draw(image)

        lightGreen = (123, 209, 72)
        lightGray = (211, 211, 211)
        lightBlack = (48, 54, 59)
        lightBlue = (173, 216, 230)
        red = (255, 0, 0)
        black = (0, 0, 0)

        fontSimple = ImageFont.truetype("repositories/bookings/open_sans.ttf", size=14)

        bookings = await self.get_bookings_for_current_week()

        for booking in bookings:
            # currentFont = fontBold if booking.Participant.Alias == participant.Alias else fontSimple

            # bookingBrush = lightGray if booking.Participant.Status == "free" else lightGreen

            day = booking.time_start.weekday()

            ylength = await count_duration(booking.time_start, booking.time_end)
            x0 = xbase + xsize * day
            y0 = ybase + int(ysize * ((booking.time_start.hour - 7) + (booking.time_start.minute / 60.0)))
            x1 = x0 + xsize
            y1 = y0 + 31.5 * ylength

            draw.rounded_rectangle((x0, y0, x1, y1), 2, fill=lightGray)
            participant = await self.get_participant(booking.participant_id)

            alias = participant.alias
            if len(alias) > 11:
                alias = alias[:11] + "..."

            caption = alias + " "

            draw.text(
                (x0 + 2, y0 + 5),
                text=f"{caption}{booking.time_start.strftime('%H:%M')}-{booking.time_end.strftime('%H:%M')}",
                fill=lightBlack,
                font=fontSimple,
            )

        today = datetime.date.today()
        weekday = today.weekday()

        current_datetime = datetime.datetime.now()

        current_hour = current_datetime.hour
        if 6 < current_hour < 23:
            now_x0 = xbase + xsize * weekday
            now_y0 = ybase + int(ysize * ((datetime.datetime.now().hour - 7) + (datetime.datetime.now().minute / 60)))
            draw.rounded_rectangle((now_x0, now_y0, now_x0 + xsize, now_y0 + 2), 2, fill=red)

        image.save("result.png")

        with open("result.png", "rb") as f:
            image_stream = io.BytesIO(f.read())

        return image_stream

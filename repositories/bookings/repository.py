import datetime
import io
from datetime import date, timedelta

from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import and_, between, delete, select
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

    async def form_schedule(self):
        xbase = 48
        ybase = 73
        xsize = 176
        ysize = 32

        # Create a new image using PIL
        image = Image.open("repositories/bookings/schedule.jpg")
        draw = ImageDraw.Draw(image)

        lightGreen = (123, 209, 72)
        lightGray = (211, 211, 211)
        lightBlue = (173, 216, 230)
        red = (255, 0, 0)
        black = (0, 0, 0)

        # Define fonts
        fontSimple = ImageFont.load_default()
        fontBold = ImageFont.load_default()

        xcorner = 0
        ycorner = 0

        # Get bookings for the week
        bookings = await self.get_bookings_for_current_week()

        today = datetime.date.today()

        day = today.weekday()

        for booking in bookings:
            # currentFont = fontBold if booking.Participant.Alias == participant.Alias else fontSimple

            # bookingBrush = lightGray if booking.Participant.Status == "free" else lightGreen

            ylength = int(ysize * (booking.TimeEnd.minute - booking.TimeStart.minute) / 60.0)
            xcorner = xbase + xsize * day
            ycorner = ybase + int(ysize * ((booking.TimeStart.hour - 7) + (booking.TimeStart.minute / 60.0)))

            draw.rectangle((xcorner, ycorner, xcorner + xsize - 10, ycorner + ylength - 5), fill=lightGray)

            caption = booking.participant_id
            # (
            #     "\n" if booking.time_end.hour - booking.time_end.hour <= 1 else " ")
            draw.text(
                (xcorner + 2, ycorner + 2),
                caption + booking.time_start.strftime("%H:%M") + " " + booking.time_end.strftime("%H:%M"),
                font=fontSimple,
                fill=black,
            )

        nowxcorner = xbase + (xsize * day)
        nowycorner = ybase + int(
            ysize * ((datetime.datetime.now().hour - 7 + 3) + (datetime.datetime.now().minute / 60.0))
        )
        draw.rectangle((nowxcorner, nowycorner, nowxcorner + xsize, nowycorner + 2), fill=red)

        # Save the image to a temporary file
        image.save("result.png")

        # Open and return the temporary file as a stream
        with open("result.png", "rb") as f:
            image_stream = io.BytesIO(f.read())

        return image_stream

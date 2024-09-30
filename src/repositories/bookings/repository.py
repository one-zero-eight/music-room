__all__ = ["booking_repository", "SqlBookingRepository"]

import datetime
import io
from datetime import datetime as datetime_datetime
from datetime import timedelta
from typing import Optional, Self

from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import and_, between, select, insert, delete, or_, not_
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import NoSuchBooking
from src.schemas import CreateBooking, ViewBooking, ViewUser
from src.storage.sql import AbstractSQLAlchemyStorage
from src.storage.sql.models import Booking, User
from src.tools import count_duration
from src.tools.utils import get_week_numbers


class SqlBookingRepository:
    storage: AbstractSQLAlchemyStorage

    def update_storage(self, storage: AbstractSQLAlchemyStorage) -> Self:
        self.storage = storage
        return self

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    async def create(self, user_id: int, booking: "CreateBooking") -> ViewBooking:
        async with self._create_session() as session:
            query = insert(Booking).values(user_id=user_id, **booking.model_dump()).returning(Booking)
            obj = await session.scalar(query)
            await session.commit()
            await session.refresh(obj)
            return ViewBooking.model_validate(obj)

    async def get_booking(self, booking_id: int) -> Optional["ViewBooking"]:
        async with self._create_session() as session:
            query = select(Booking).where(Booking.id == booking_id)
            obj = await session.scalar(query)
            if obj:
                return ViewBooking.model_validate(obj)
            else:
                return None

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

    async def check_collision(self, time_start: datetime.datetime, time_end: datetime.datetime) -> ViewBooking | None:
        async with self._create_session() as session:
            query = select(Booking).where(
                not_(
                    or_(
                        and_(
                            Booking.time_start < time_start,
                            Booking.time_end <= time_start,
                        ),
                        and_(Booking.time_start >= time_end, Booking.time_end > time_end),
                    )
                )
            )
            collision = await session.scalar(query)
            if collision:
                return ViewBooking.model_validate(collision)

    async def get_user(self, user_id) -> ViewUser:
        async with self._create_session() as session:
            query = select(User).where(User.id == user_id)
            obj = await session.scalar(query)
            return ViewUser.model_validate(obj)

    async def draw_week_numbers(self, draw: ImageDraw, current_week: bool):
        fontSimple = ImageFont.truetype("src/repositories/bookings/open_sans.ttf", size=14)
        lightBlack = (48, 54, 59)

        weekdays_numbers, wide = await get_week_numbers(current_week)

        x_coord = 130
        y_coord = 30
        week_days = 7
        offset = 175 if wide else 176

        draw.text(
            (x_coord, y_coord),
            text=f"{weekdays_numbers[0]}",
            fill=lightBlack,
            font=fontSimple,
        )

        for i in range(1, week_days):
            draw.text(
                (x_coord + offset * i, y_coord),
                text=f"{weekdays_numbers[i]}",
                fill=lightBlack,
                font=fontSimple,
            )

    async def draw_month_and_year(self, draw: ImageDraw, current_week: bool):
        fontSimple = ImageFont.truetype("src/repositories/bookings/open_sans.ttf", size=14)
        lightBlack = (48, 54, 59)

        offset = 7 if not current_week else 0
        current_datetime = datetime.datetime.now() + datetime.timedelta(offset)
        current_year = current_datetime.year
        current_month = current_datetime.strftime("%b")
        draw.text(
            (12, 12),
            text=f"{current_month} {current_year}",
            fill=lightBlack,
            font=fontSimple,
        )

    async def is_start_of_week(self, start_of_week: datetime.date):
        today = datetime.datetime.now()

        return (today - timedelta(days=today.weekday())).date() == start_of_week

    async def form_schedule(self, start_of_week: datetime.date) -> bytes:
        xbase = 48  # origin for x
        ybase = 73  # origin for y
        xsize = round(175.5)  # length of the rect by x-axis
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
            ylength = count_duration(booking.time_start, booking.time_end)

            cell_canvas = Image.new("RGB", (xsize, int(ysize * ylength)), "white")
            cell_canvas_painter = ImageDraw.Draw(cell_canvas)
            day = booking.time_start.weekday()

            x0 = xbase + xsize * day
            y0 = ybase + int(ysize * ((booking.time_start.hour - 7) + (booking.time_start.minute / 60.0)))

            cell_canvas_painter.rounded_rectangle(
                (0, 0, cell_canvas.width - 1, cell_canvas.height - 1), 2, fill=lightGray, outline=lightBlack, width=2
            )
            user = await self.get_user(booking.user_id)
            caption = user.alias

            # noinspection SqlAlchemyUnsafeQuery
            cell_canvas_painter.text(
                (8, cell_canvas.height / 2 - 9),
                text=caption,
                fill=lightBlack,
                font=fontSimple,
            )

            time_canvas = Image.new("RGBA", (xsize, ysize), (0, 0, 0, 0))
            time_canvas_painter = ImageDraw.Draw(time_canvas)

            time_canvas_painter.text(
                (9, 0),
                text=f"{booking.time_start.strftime('%H:%M')}-{booking.time_end.strftime('%H:%M')}",
                fill=lightBlack,
                font=fontSimple,
            )

            time_canvas_rect = time_canvas.getbbox()
            cell_canvas_painter.rectangle(
                (
                    cell_canvas.width - time_canvas_rect[2] + time_canvas_rect[0] - 14,
                    2,
                    cell_canvas.width - 3,
                    cell_canvas.height - 3,
                ),
                lightGray,
            )
            cell_canvas.paste(
                time_canvas,
                (cell_canvas.width - time_canvas_rect[2] + time_canvas_rect[0] - 17, cell_canvas.height // 2 - 9),
                time_canvas,
            )

            image.paste(cell_canvas, (int(x0), y0))

        today = datetime.date.today()
        weekday = today.weekday()

        current = datetime.datetime.now()
        current_week = False
        if start_of_week <= current.date() <= start_of_week + timedelta(days=6):
            current_week = True

        # Drawing red line
        if 6 < current.hour < 23 and current_week:
            now_x0 = xbase + xsize * weekday
            now_y0 = ybase + int(ysize * ((current.hour - 7) + (current.minute / 60)))
            draw.rounded_rectangle((now_x0, now_y0, now_x0 + xsize, now_y0 + 2), 2, fill=red)

        await self.draw_week_numbers(draw, await self.is_start_of_week(start_of_week))
        await self.draw_month_and_year(draw, current_week)
        image_stream = io.BytesIO()
        image.save(image_stream, format="png")
        val = image_stream.getvalue()
        image_stream.close()
        return val

    async def get_daily_bookings(self, date: datetime.date) -> list[ViewBooking]:
        async with self._create_session() as session:
            start_of_day = datetime_datetime.combine(date, datetime.time.min)
            end_of_day = datetime_datetime.combine(date, datetime.time.max)

            query = select(Booking).where(and_(Booking.time_start >= start_of_day, Booking.time_end <= end_of_day))

            objs = await session.scalars(query)

            return [ViewBooking.model_validate(obj) for obj in objs]

    async def get_bookings(self, from_date: datetime.date | None = None, to_date: datetime.date | None = None):
        async with self._create_session() as session:
            query = select(Booking)
            if from_date:
                query = query.where(Booking.time_start >= datetime.datetime.combine(from_date, datetime.time.min))
            if to_date:
                query = query.where(Booking.time_end <= datetime.datetime.combine(to_date, datetime.time.max))
            objs = await session.scalars(query)
            return [ViewBooking.model_validate(obj) for obj in objs]

    async def get_user_bookings(self, user_id: int) -> list[ViewBooking]:
        async with self._create_session() as session:
            query = select(Booking).where(Booking.user_id == user_id)
            objs = await session.scalars(query)
            return [ViewBooking.model_validate(obj) for obj in objs]


booking_repository: SqlBookingRepository = SqlBookingRepository()

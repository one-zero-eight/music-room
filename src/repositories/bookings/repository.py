__all__ = ["booking_repository", "SqlBookingRepository"]

import datetime
import io
from datetime import datetime as datetime_datetime
from datetime import timedelta
from pathlib import Path
from typing import Optional, Self

from cairosvg import svg2png
from sqlalchemy import and_, between, delete, insert, not_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import NoSuchBooking
from src.repositories.users.repository import user_repository
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

    async def is_start_of_week(self, start_of_week: datetime.date):
        today = datetime.datetime.now()

        return (today - timedelta(days=today.weekday())).date() == start_of_week

    async def form_schedule(self, start_of_week: datetime.date, from_user_id: int) -> bytes:
        with open(Path(__file__).parent / "resources/Plain.svg", encoding="utf-8") as file:
            svg_string = file.read()

        end = svg_string.index("</tspan>", svg_string.index("month"))
        svg_string = f"{svg_string[:end]}{dict({
            1: "Jan",
            2: "Feb",
            3: "Mar",
            4: "Apr",
            5: "May",
            6: "Jun",
            7: "Jul",
            8: "Aug",
            9: "Sep",
            10: "Oct",
            11: "Nov",
            12: "Dec"
        })[datetime.date.today().month]}{svg_string[end:]}"

        end = svg_string.index("</tspan>", svg_string.index("monthnum"))
        svg_string = f"{svg_string[:end]}{datetime.date.today().year % 100}{svg_string[end:]}"

        weekdays_numbers, wide = await get_week_numbers(await self.is_start_of_week(start_of_week))
        today = datetime.datetime.today().day

        for i, (number, identifier) in enumerate(
            zip(weekdays_numbers, "monnum tuenum wednum thunum frinum satnum sunnum".split())
        ):
            text = f"""
            <tspan
            x="{266.9544915 + (0 if i == 0 else 126.16007 if i == 1 else 122.16095 * (i - 1) + 126.16007)}"
            y="{66}" style="font-style:normal;
            font-variant:normal;font-weight:bold;font-stretch:normal;font-size:20px;font-family:Roboto;
            text-align:start;text-anchor:middle;fill:#000000;
            fill-opacity:1;stroke:none">{identifier[:3].capitalize()} {number}</tspan>
            """

            end = svg_string.rfind("/>") + 2
            svg_string = svg_string[:end] + text + svg_string[end:]

            if today == number:
                end = svg_string.index(identifier[:3])
                end = svg_string.rfind('"opacity:', 0, end) + 8
                svg_string = f"{svg_string[:end]}1{svg_string[end + 1:]}"

        character_widths = {
            "a": 11.2,
            "b": 11.2,
            "c": 10.4,
            "d": 11.13,
            "e": 11.2,
            "f": 8,
            "g": 11.13,
            "h": 11.13,
            "i": 4.45,
            "j": 6.05,
            "k": 10.4,
            "l": 4.45,
            "m": 16.66,
            "n": 11.13,
            "o": 11.2,
            "p": 11.2,
            "q": 11.13,
            "r": 7.2,
            "s": 10,
            "t": 6.4,
            "u": 11.13,
            "v": 10.4,
            "w": 16,
            "x": 11.2,
            "y": 10.4,
            "z": 10.4,
            "A": 14.4,
            "B": 13.35,
            "C": 14.45,
            "D": 14.45,
            "E": 13.45,
            "F": 12.23,
            "G": 15.56,
            "H": 14.45,
            "I": 5.56,
            "J": 10,
            "K": 13.6,
            "L": 11.2,
            "M": 16.66,
            "N": 14.45,
            "O": 15.56,
            "P": 13.35,
            "Q": 15.56,
            "R": 14.45,
            "S": 13.35,
            "T": 12.8,
            "U": 14.45,
            "V": 14.4,
            "W": 19.2,
            "X": 14.4,
            "Y": 14.4,
            "Z": 12.23,
            "0": 11.13,
            "1": 11.13,
            "2": 11.13,
            "3": 11.2,
            "4": 11.13,
            "5": 11.2,
            "6": 11.2,
            "7": 11.2,
            "8": 11.2,
            "9": 11.2,
            "_": 12.8,
        }

        bookings = await self.get_bookings_for_week(start_of_week)
        current_hour = datetime.datetime.now().hour
        cell_size = [124.161, 83.451]
        middle_offset = 17.739
        try:
            end = svg_string.index(f"i{current_hour}")
            end = svg_string.rfind('"opacity:', 0, end) + 8
            svg_string = f"{svg_string[:end]}1{svg_string[end + 1:]}"
        except ValueError:
            pass
        for booking in bookings:
            duration = count_duration(booking.time_start, booking.time_end)
            day = booking.time_start.weekday()
            coordinates = [
                (cell_size[0] - 2) * day,
                (cell_size[1] - 2) * ((booking.time_start.hour - 7) + booking.time_start.minute / 60),
            ]

            user = await user_repository.get_user(booking.user_id)

            symbol = f"""<svg x="{coordinates[0]}" y="{coordinates[1]}">
            <rect style="opacity:1;
            fill:{"#cbe7cb" if user.telegram_id == from_user_id else "#e5e2e5"};
            fill-opacity:1;stroke:#e5e2e5;stroke-width:2;
            stroke-linecap:round;stroke-linejoin:round;
            stroke-opacity:1"
            width="122.16101" height="{duration * (cell_size[1] - 2)}"
            x="207.87349" y="119.77097"
            rx="0" ry="0"/></svg>"""
            perceptual_text_y_offset = 5
            perceptual_text_x_offset = -33.5
            text_time_symbol = f"""
            <tspan x="{268.955 + coordinates[0] + perceptual_text_x_offset}"
            y="{119.77097 + coordinates[1] + duration * (cell_size[1] - 2) / 2 + perceptual_text_y_offset}"
            style="font-style:normal;font-variant:normal;font-weight:normal;
            font-stretch:normal;font-family:'Roboto';text-align:start;text-anchor:middle;
            fill:#000000;fill-opacity:1;stroke:none;font-size:20px">
            {booking.time_start.strftime('%H:%M')}-{booking.time_end.strftime('%H:%M')}</tspan>"""
            text_alias_symbol = ""
            if duration > 0.5:
                max_width = 112
                alias = ""
                current_width = 0
                for elem in user.alias:
                    if (current_width := current_width + character_widths[elem]) <= max_width:
                        alias += elem
                    else:
                        break
                text_alias_symbol = f"""
            <tspan id="tspan89" x="{268.955 + coordinates[0] + perceptual_text_x_offset}"
            y="{119.77097 + coordinates[1] + duration * (cell_size[1] - 2) / 2
                + perceptual_text_y_offset * 2 + middle_offset}"
            style="font-style:normal;font-variant:normal;font-weight:normal;
            font-stretch:normal;font-family:'Roboto';text-anchor:middle;
            fill:#000000;fill-opacity:1;stroke:none;font-size:20px">
            {alias}</tspan>"""
            end = svg_string.rfind("<")
            svg_string = f"{svg_string[:end]}{symbol}{text_alias_symbol}{text_time_symbol}{svg_string[end:]}"

        # mark current time with red
        end = svg_string.rfind("<")
        height = 2
        symbol = f"""<svg x="{(cell_size[0] - 2) * datetime.datetime.today().weekday()}"
                    y="{((cell_size[1] - 2) * 17) *
                        (datetime.datetime.today().hour + datetime.datetime.today().minute / 60 - 7) / 17}">
                    <rect style="opacity:1;
                    fill:#d31109;
                    fill-opacity:1;stroke:#d31109;stroke-width:2;
                    stroke-linecap:round;stroke-linejoin:round;
                    stroke-opacity:1"
                    width="122.16101" height="{height}"
                    x="207.87349" y="119.77097"
                    rx="0" ry="0"/></svg>"""
        svg_string = f"""{svg_string[:end]}{symbol}{svg_string[end:]}"""

        # add schedule table border
        end = svg_string.rfind("<")
        svg_string = f"""{svg_string[:end]}<path
            style="color:#000000;fill:#ffffff;fill-opacity:1;stroke:none;stroke-linecap:round;
            stroke-linejoin:round;stroke-opacity:1;-inkscape-stroke:none"
            d="m 227.87305,118.77148 c -11.61669,0 -21,9.38331 -21,21 V 1485.4492 c 0,11.6167 9.38331,21 21,21 H
            1043 c 11.6167,0 21,-9.3833 21,-21 V 139.77148 c 0,-11.61669 -9.3833,-21 -21,-21 z M 192.87389,104.72179 H
            1080 v 0 V 1520 v 0 H 192.87389 v 0 z"
            />{svg_string[end:]}"""
        open("TEST.svg", "w").write(svg_string)
        image_stream = io.BytesIO()
        svg2png(bytestring=svg_string, write_to=image_stream, scale=2)
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

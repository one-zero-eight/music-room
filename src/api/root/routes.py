__all__ = ["router"]

import datetime
from zlib import crc32

import icalendar
from fastapi import APIRouter, Response

from src.dependendies.auth import VerifiedDep
from src.exceptions import ForbiddenException
from src.repositories.bookings.repository import booking_repository
from src.schemas.auth import VerificationSource

router = APIRouter(tags=["Root"])


def _calendar_baseline():
    main_calendar = icalendar.Calendar(
        prodid="-//one-zero-eight//InNoHassle Schedule",
        version="2.0",
        method="PUBLISH",
    )
    main_calendar["x-wr-calname"] = "Music Room schedule from innohassle.ru"
    main_calendar["x-wr-timezone"] = "Europe/Moscow"
    main_calendar["x-wr-caldesc"] = "Generated by InNoHassle Schedule"
    return main_calendar


def _booking_to_vevent(booking, is_personal=False):
    string_to_hash = str(booking.id)
    hash_ = crc32(string_to_hash.encode("utf-8"))
    uid = f"music-room-{abs(hash_):x}@innohassle.ru"

    vevent = icalendar.Event()
    vevent.add("uid", uid)
    vevent.add("dtstart", icalendar.vDatetime(booking.time_start))
    vevent.add("dtend", icalendar.vDatetime(booking.time_end))
    vevent.add("location", "Music room 020")
    vevent.add("description", f"Booked by https://t.me/{booking.user_alias}")
    if is_personal:
        vevent.add("summary", "Music room")
    else:
        vevent.add("summary", f"Booking @{booking.user_alias}")
    return vevent


@router.get(
    "/music-room.ics",
    responses={
        200: {
            "description": "ICS file with schedule of the music room",
            "content": {"text/calendar": {"schema": {"type": "string", "format": "binary"}}},
        },
    },
    response_class=Response,
    tags=["ICS"],
)
async def get_music_room_ics():
    main_calendar = _calendar_baseline()

    from_date = datetime.date.today() - datetime.timedelta(days=14)
    to_date = datetime.date.today() + datetime.timedelta(days=14)
    bookings = await booking_repository.get_bookings(from_date, to_date)
    dtstamp = icalendar.vDatetime(datetime.datetime.now())
    for booking in bookings:
        vevent = _booking_to_vevent(booking)
        vevent.add("dtstamp", dtstamp)
        main_calendar.add_component(vevent)

    ical_bytes = main_calendar.to_ical()

    return Response(content=ical_bytes, media_type="text/calendar")


@router.get(
    "/users/{user_id}/bookings.ics",
    responses={
        200: {
            "description": "ICS file with schedule of the user",
            "content": {"text/calendar": {"schema": {"type": "string", "format": "binary"}}},
        },
    },
    response_class=Response,
    tags=["Users", "ICS"],
)
async def get_user_ics(user_id: int, verification: VerifiedDep):
    if verification.source == VerificationSource.BOT and user_id != verification.telegram_id:
        raise ForbiddenException()

    main_calendar = _calendar_baseline()
    bookings = await booking_repository.get_user_bookings(user_id)
    dtstamp = icalendar.vDatetime(datetime.datetime.now())
    for booking in bookings:
        vevent = _booking_to_vevent(booking, is_personal=True)
        vevent.add("dtstamp", dtstamp)
        main_calendar.add_component(vevent)

    ical_bytes = main_calendar.to_ical()
    return Response(content=ical_bytes, media_type="text/calendar")

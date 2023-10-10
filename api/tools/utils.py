import datetime
from datetime import datetime as dt

from cryptography.fernet import Fernet

from api.exceptions import InvalidParticipantStatus


def max_hours_to_book_per_day(status: str):
    if status == "Lord":
        return 15
    elif status == "Senior":
        return 4
    elif status in ("Investor", "Middle", "payer"):
        return 3
    elif status in ("Freelance", "free", "Junior"):
        return 2
    raise InvalidParticipantStatus()


def max_hours_to_book_per_week(status: str):
    if status == "Lord":
        return 150
    elif status == "Senior":
        return 8
    elif status in ("Investor", "Middle", "payer"):
        return 6
    elif status in ("Freelance", "free", "Junior"):
        return 4
    raise InvalidParticipantStatus()


async def count_duration(start_time: datetime.datetime, end_time: datetime.datetime):
    duration = end_time - start_time
    seconds = duration.seconds
    minutes = seconds // 60
    hours = minutes / 60
    return hours


async def fix_time_end(time_end: datetime.datetime):
    return time_end - datetime.timedelta(minutes=1)


async def get_date_from_str(date: str):
    try:
        return dt.strptime(date, "%d.%m.%Y").date()
    except ValueError:
        return "Invalid date format. Use the format 'dd.mm.yyyy'"


async def is_sc_working(start_time: datetime.datetime, end_time: datetime.datetime):
    if start_time.hour < 7 or (end_time.hour > 22 and end_time.minute > 30):
        return 0
    return 1

import datetime

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
        return 14
    raise InvalidParticipantStatus()


async def count_duration(start_time: datetime.datetime, end_time: datetime.datetime):
    duration = end_time - start_time
    seconds = duration.seconds
    minutes = seconds // 60
    hours = minutes / 60
    return hours


async def fix_time_end(time_end: datetime.datetime):
    return time_end - datetime.timedelta(minutes=1)

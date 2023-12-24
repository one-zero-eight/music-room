import datetime


def count_duration(start_time: datetime.datetime, end_time: datetime.datetime):
    duration = end_time - start_time
    seconds = duration.seconds
    minutes = seconds // 60 - 1
    hours = minutes / 60
    return hours


async def is_sc_working(start_time: datetime.datetime, end_time: datetime.datetime):
    if start_time.hour < 7 or (end_time.hour > 22 and end_time.minute > 30):
        return 0
    return 1

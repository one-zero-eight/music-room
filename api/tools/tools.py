import datetime


def max_hours_to_book_per_day(status: str):
    if status == "Lord":
        return 15
    elif status == "Senior":
        return 4
    elif status in ("Investor", "Middle", "payer"):
        return 3
    elif status in ("Freelance", "free", "Junior"):
        return 2
    # Raise an exception for an invalid status
    return 0


def max_hours_to_book_per_week(status: str):
    if status == "Lord":
        return 150
    elif status == "Senior":
        return 8
    elif status in ("Investor", "Middle", "payer"):
        return 6
    elif status in ("Freelance", "free", "Junior"):
        return 4
        # Raise an exception for an invalid status
    return 0


def count_duration(start_time: datetime.datetime, end_time: datetime.datetime):
    duration = end_time - start_time
    lst = list(str(duration).split(":"))
    return format(float(lst[0]) + float(lst[1]) / 60, ".2f")

from fastapi import HTTPException
from starlette import status


class CollisionInBooking(HTTPException):
    """
    HTTP_409_CONFLICT
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="There exists one more booking that intersects current",
        )


class NotEnoughHoursToBook(HTTPException):
    """
    HTTP_409_CONFLICT
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Not enough hours to book",
        )

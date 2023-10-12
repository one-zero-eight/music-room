import datetime

from pydantic import BaseModel, ConfigDict

__all__ = ["CreateBooking", "ViewBooking", "HelpBooking"]


class CreateBooking(BaseModel):
    participant_id: int
    time_start: datetime.datetime
    time_end: datetime.datetime


class ViewBooking(BaseModel):
    id: int
    participant_id: int
    time_start: datetime.datetime
    time_end: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class HelpBooking(BaseModel):
    time_start: datetime.datetime
    time_end: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

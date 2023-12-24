import datetime

from pydantic import BaseModel, ConfigDict, NaiveDatetime, Field

__all__ = ["CreateBooking", "ViewBooking", "HelpBooking"]

_now = datetime.datetime.now().replace(second=0, microsecond=0, tzinfo=None)


class CreateBooking(BaseModel):
    participant_id: int
    time_start: NaiveDatetime = Field(..., example=_now)
    time_end: NaiveDatetime = Field(..., example=_now + datetime.timedelta(hours=1))


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

import datetime

from pydantic import BaseModel, ConfigDict, Field, NaiveDatetime, model_validator

__all__ = ["CreateBooking", "ViewBooking", "ViewBooking"]

_now = datetime.datetime.now().replace(second=0, microsecond=0, tzinfo=None)


class CreateBooking(BaseModel):
    time_start: NaiveDatetime = Field(..., example=_now)
    time_end: NaiveDatetime = Field(..., example=_now + datetime.timedelta(hours=1))

    @model_validator(mode="after")
    def order_times(self):
        if self.time_start >= self.time_end:
            raise ValueError("`time_start` must be less than `time_end`")
        return self


class ViewBooking(BaseModel):
    id: int
    user_id: int
    user_alias: str
    time_start: datetime.datetime
    time_end: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

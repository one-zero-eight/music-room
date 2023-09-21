import datetime

from pydantic import BaseModel, ConfigDict, Field

from schemas import ViewBooking


class CreateParticipant(BaseModel):
    name: str
    alias: str
    status: str


class ViewParticipantBeforeBooking(BaseModel):
    id: int
    name: str
    alias: str
    status: str
    # max_hours_per_day: int
    # max_hours_per_week: int

    model_config = ConfigDict(from_attributes=True)


class ViewParticipantAfterBooking(BaseModel):
    id: int
    name: str
    alias: str
    status: str
    # max_hours_per_day: int
    # max_hours_per_week: int

    booking: list["ViewBooking"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

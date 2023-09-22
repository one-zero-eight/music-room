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
    daily_hours: int
    weekly_hours: int

    model_config = ConfigDict(from_attributes=True)


class ViewParticipantAfterBooking(BaseModel):
    id: int
    name: str
    alias: str
    status: str
    daily_hours: int
    weekly_hours: int

    booking: list["ViewBooking"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

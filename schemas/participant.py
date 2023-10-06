from pydantic import BaseModel, ConfigDict, Field

from schemas import ViewBooking


class CreateParticipant(BaseModel):
    name: str = ""
    alias: str = ""
    email: str
    phone_number: str = ""
    status: str
    need_to_fill_profile: bool


class FillParticipantProfile(BaseModel):
    name: str = ""
    alias: str = ""
    email: str
    phone_number: str = ""


class ViewParticipantBeforeBooking(BaseModel):
    id: int
    name: str = None
    alias: str = None
    email: str
    phone_number: str = None
    status: str
    need_to_fill_profile: bool

    model_config = ConfigDict(from_attributes=True)


class ViewParticipantAfterBooking(BaseModel):
    id: int
    name: str
    alias: str
    email: str
    phone_number: str
    status: str
    need_to_fill_profile: bool

    booking: list["ViewBooking"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

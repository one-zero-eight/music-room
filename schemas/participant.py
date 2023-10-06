from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from schemas import ViewBooking


class CreateParticipant(BaseModel):
    name: Optional[str] = None
    alias: Optional[str] = None
    email: str
    phone_number: Optional[str] = None
    status: str
    need_to_fill_profile: bool


class FillParticipantProfile(BaseModel):
    name: Optional[str] = None
    alias: Optional[str] = None
    email: str
    phone_number: Optional[str] = None


class ViewParticipantBeforeBooking(BaseModel):
    id: int
    name: Optional[str] = None
    alias: Optional[str] = None
    email: str
    phone_number: Optional[bytes] = None
    status: str
    need_to_fill_profile: bool

    model_config = ConfigDict(from_attributes=True)


class ViewParticipantAfterBooking(BaseModel):
    id: int
    name: str
    alias: str
    email: str
    phone_number: Optional[bytes] = None
    status: str
    need_to_fill_profile: bool

    booking: list["ViewBooking"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

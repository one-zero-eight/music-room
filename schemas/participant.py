from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from schemas import ViewBooking


class CreateParticipant(BaseModel):
    name: Optional[str] = None
    alias: Optional[str] = None
    email: str
    phone_number: Optional[str] = None
    telegram_id: Optional[str] = None
    status: str
    need_to_fill_profile: bool


class FillParticipantProfile(BaseModel):
    name: Optional[str] = None
    email: str
    alias: Optional[str] = None
    telegram_id: Optional[str] = None
    phone_number: Optional[str] = None


class ViewParticipantBeforeBooking(BaseModel):
    id: int
    name: Optional[str] = None
    alias: Optional[str] = None
    email: str
    phone_number: Optional[bytes] = None
    telegram_id: Optional[str] = None
    status: str
    need_to_fill_profile: bool

    model_config = ConfigDict(from_attributes=True)

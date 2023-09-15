from pydantic import BaseModel, Field

from schemas import ViewBooking


class CreateParticipant(BaseModel):
    name: str
    alias: str
    selected_date: str
    status: str


class ViewParticipant(BaseModel):
    id: int
    name: str
    alias: str
    selected_date: str
    status: str

    tags: list["ViewBooking"] = Field(default_factory=list)

    class Config:
        validate_default = True

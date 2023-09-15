from pydantic import BaseModel, Field, ConfigDict
import datetime
from schemas import ViewBooking


class CreateParticipant(BaseModel):
    name: str
    alias: str
    selected_date: datetime.datetime
    status: str


class ViewParticipantBeforeBooking(BaseModel):
    id: int
    name: str
    alias: str
    selected_date: datetime.datetime
    status: str

    # booking: list["ViewBooking"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

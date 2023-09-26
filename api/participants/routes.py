from api.dependencies import PARTICIPANT_REPOSITORY_DEPENDENCY
from api.exceptions import InvalidParticipantStatus
from api.participants import router
from api.tools.tools import max_hours_to_book_per_day as status_validate
from schemas import (CreateParticipant, ViewBooking,
                     ViewParticipantBeforeBooking)


@router.post("/create")
async def create_participant(
    participant: CreateParticipant,
    participant_repository: PARTICIPANT_REPOSITORY_DEPENDENCY,
) -> ViewParticipantBeforeBooking:
    try:
        status_validate(participant.status)
    except InvalidParticipantStatus:
        raise InvalidParticipantStatus()

    created = await participant_repository.create(participant)
    return created


@router.put("/{participant_id}/status")
async def change_status(
    participant_id: int,
    new_status: str,
    participant_repository: PARTICIPANT_REPOSITORY_DEPENDENCY,
) -> ViewParticipantBeforeBooking | str:
    try:
        status_validate(new_status)
    except InvalidParticipantStatus:
        raise InvalidParticipantStatus()

    updated_participant = await participant_repository.change_status(participant_id, new_status)
    return updated_participant


@router.get("/{participant_id}/bookings")
async def get_bookings(
    participant_id: int, participant_repository: PARTICIPANT_REPOSITORY_DEPENDENCY
) -> list[ViewBooking]:
    bookings = await participant_repository.get_participant_bookings(participant_id)
    return bookings

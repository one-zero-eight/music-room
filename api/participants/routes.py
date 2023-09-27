import datetime

from api.dependencies import PARTICIPANT_REPOSITORY_DEPENDENCY
from api.exceptions import InvalidDateFormat, InvalidParticipantStatus
from api.participants import router
from api.tools.tools import get_date_from_str
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
async def get_participant_bookings(
        participant_id: int, participant_repository: PARTICIPANT_REPOSITORY_DEPENDENCY
) -> list[ViewBooking]:
    bookings = await participant_repository.get_participant_bookings(participant_id)
    return bookings


@router.get("/{participant_id}/remaining_weekly_hours")
async def get_remaining_weekly_hours(
        participant_id: int, participant_repository: PARTICIPANT_REPOSITORY_DEPENDENCY
) -> float:
    ans = await participant_repository.get_remaining_weekly_hours(participant_id)
    return ans


@router.get("/{participant_id}/remaining_daily_hours")
async def get_remaining_daily_hours(
        participant_id: int, date: str, participant_repository: PARTICIPANT_REPOSITORY_DEPENDENCY
) -> float:
    try:
        parsed_date = await get_date_from_str(date)
        ans = await participant_repository.get_remaining_daily_hours(participant_id, parsed_date)
    except ValueError:
        raise InvalidDateFormat()
    return ans

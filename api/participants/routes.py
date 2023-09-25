from api.dependencies import PARTICIPANT_REPOSITORY_DEPENDENCY
from api.participants import router
from schemas import CreateParticipant, ViewBooking, ViewParticipantBeforeBooking


@router.post("/create")
async def create_participant(
    participant: CreateParticipant,
    participant_repository: PARTICIPANT_REPOSITORY_DEPENDENCY,
) -> ViewParticipantBeforeBooking:
    created = await participant_repository.create(participant)
    return created


@router.put("/{participant_id}/daily_hours")
async def change_daily_hours(
    participant_id: int,
    new_hours: int,
    participant_repository: PARTICIPANT_REPOSITORY_DEPENDENCY,
) -> ViewParticipantBeforeBooking:
    changed_participant = await participant_repository.change_daily_hours(participant_id, new_hours)
    return changed_participant


@router.put("/{participant_id}/weekly_hours")
async def change_weekly_hours(
    participant_id: int,
    new_hours: int,
    participant_repository: PARTICIPANT_REPOSITORY_DEPENDENCY,
) -> ViewParticipantBeforeBooking:
    changed_participant = await participant_repository.change_weekly_hours(participant_id, new_hours)
    return changed_participant


@router.put("/{participant_id}/status")
async def change_status(
    participant_id: int,
    new_status: str,
    participant_repository: PARTICIPANT_REPOSITORY_DEPENDENCY,
) -> ViewParticipantBeforeBooking | str:
    from api.tools.tools import max_hours_to_book_per_day as status_validate

    if status_validate(new_status) != 0:
        updated_participant = await participant_repository.change_status(participant_id, new_status)
        return updated_participant
    else:
        return "Invalid status"


@router.get("/{participant_id}/bookings")
async def get_bookings(
    participant_id: int, participant_repository: PARTICIPANT_REPOSITORY_DEPENDENCY
) -> list[ViewBooking]:
    bookings = await participant_repository.get_participant_bookings(participant_id)
    return bookings

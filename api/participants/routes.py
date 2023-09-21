from api.dependencies import PARTICIPANT_REPOSITORY_DEPENDENCY
from api.participants import router
from schemas import CreateParticipant, ViewParticipantBeforeBooking


@router.post("/create")
async def create_participant(
    participant: CreateParticipant,
    participant_repository: PARTICIPANT_REPOSITORY_DEPENDENCY,
) -> ViewParticipantBeforeBooking:
    created = await participant_repository.create(participant)
    return created


# @router.put("/{participant_id}/daily_hours")
# async def change_daile_hours(
#         participant_id: int,
#         new_hours: int,
#         participant_repository: PARTICIPANT_REPOSITORY_DEPENDENCY) -> ViewParticipantBeforeBooking:
#     changed_participant =


@router.put("/{participant_id}/status")
async def change_status(
    participant_id: int,
    new_status: str,
    participant_repository: PARTICIPANT_REPOSITORY_DEPENDENCY,
) -> ViewParticipantBeforeBooking | str:
    from api.tools.validation import max_hours_to_book_per_day as validate

    if validate(new_status):
        updated_participant = await participant_repository.change_status(
            participant_id, new_status
        )
        return updated_participant
    else:
        return "Invalid status"

from api.dependencies import PARTICIPANT_REPOSITORY_DEPENDENCY
from api.participants import router
from schemas import CreateParticipant, ViewParticipantBeforeBooking


@router.post("/")
async def create_participant(
    participant: CreateParticipant,
    participant_repository: PARTICIPANT_REPOSITORY_DEPENDENCY,
) -> ViewParticipantBeforeBooking:
    created = await participant_repository.create(participant)
    return created

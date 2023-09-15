from api.dependencies import PARTICIPANT_REPOSITORY_DEPENDENCY
from api.participants import router
from schemas import CreateParticipant, ViewParticipant


@router.post("/", response_model=None)
async def create_participant(
    participant: CreateParticipant,
    participant_repository: PARTICIPANT_REPOSITORY_DEPENDENCY,
) -> ViewParticipant:
    created = await participant_repository.create(participant)
    return created

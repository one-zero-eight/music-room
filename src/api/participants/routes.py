import datetime
from typing import Optional

from fastapi import Query

from src.api.dependencies import Dependencies, VerifiedDep
from src.api.participants import router
from src.exceptions import ForbiddenException
from src.repositories.participants.abc import AbstractParticipantRepository
from src.schemas import ViewBooking, ViewParticipant, ParticipantStatus, FillParticipantProfile


@router.put("/{participant_id}/status")
async def change_status(
    participant_id: int,
    new_status: ParticipantStatus,
    verified: VerifiedDep,
) -> ViewParticipant:
    participant_repository = Dependencies.get(AbstractParticipantRepository)

    source = await participant_repository.get_participant(verified.user_id)
    if source.status != ParticipantStatus.LORD:
        raise ForbiddenException()

    updated_participant = await participant_repository.change_status(participant_id, new_status)
    return updated_participant


@router.get("/me")
async def get_me(verified: VerifiedDep) -> ViewParticipant:
    participant_repository = Dependencies.get(AbstractParticipantRepository)
    participant = await participant_repository.get_participant(verified.user_id)
    return participant


@router.post("/me/fill_profile")
async def fill_profile(
    participant: FillParticipantProfile,
    verified: VerifiedDep,
) -> ViewParticipant:
    participant_repository = Dependencies.get(AbstractParticipantRepository)
    created = await participant_repository.fill_profile(verified.user_id, participant)
    return created


@router.get("/me/bookings")
async def get_participant_bookings(verified: VerifiedDep) -> list[ViewBooking]:
    participant_repository = Dependencies.get(AbstractParticipantRepository)
    bookings = await participant_repository.get_participant_bookings(verified.user_id)
    return bookings


@router.get("/me/remaining_weekly_hours")
async def get_remaining_weekly_hours(verified: VerifiedDep) -> float:
    participant_repository = Dependencies.get(AbstractParticipantRepository)
    ans = await participant_repository.remaining_weekly_hours(verified.user_id)
    return ans


@router.get("/me/remaining_daily_hours")
async def get_remaining_daily_hours(
    verified: VerifiedDep,
    date: Optional[datetime.date] = Query(
        default_factory=datetime.date.today,
        example=datetime.date.today().isoformat(),
        description="Date for which to get remaining hours (iso format). Default: server-side today",
    ),
) -> float:
    participant_repository = Dependencies.get(AbstractParticipantRepository)
    ans = await participant_repository.remaining_daily_hours(verified.user_id, date)
    return ans


@router.get("/participant_id")
async def get_participant_id(telegram_id: str) -> int:
    participant_repository = Dependencies.get(AbstractParticipantRepository)

    res = await participant_repository.get_participant_id(telegram_id)
    return res

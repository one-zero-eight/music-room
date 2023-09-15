from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.participants.abc import AbstractParticipantRepository
from schemas import CreateParticipant, ViewParticipantBeforeBooking
from storage.sql import AbstractSQLAlchemyStorage
from storage.sql.models import Participant


class SqlParticipantRepository(AbstractParticipantRepository):
    storage: AbstractSQLAlchemyStorage

    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    # ----------------- CRUD ----------------- #

    async def create(
        self, participant: "CreateParticipant"
    ) -> "ViewParticipantBeforeBooking":
        async with self._create_session() as session:
            query = (
                insert(Participant)
                .values(**participant.model_dump())
                .returning(Participant)
            )
            obj = await session.scalar(query)
            await session.commit()
            return ViewParticipantBeforeBooking.model_validate(obj)

    # async def read(self, event_id: int) -> "ViewEvent":
    #     async with self._create_session() as session:
    #         return await CRUD.read(session, id=event_id)
    #
    # async def update(self, event_id: int, event: "UpdateEvent") -> "ViewEvent":
    #     async with self._create_session() as session:
    #         return await CRUD.update(session, event, id=event_id)
    #
    # async def delete(self, event_id: int) -> None:
    #     async with self._create_session() as session:
    #         await CRUD.delete(session, id=event_id)
    #
    # # ^^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^ #
    # # ----------------- PATCHES ----------------- #
    # async def add_patch(self, event_id: int, patch: "AddEventPatch") -> "ViewEventPatch":
    #     async with self._create_session() as session:
    #         q = (
    #             postgres_insert(EventPatch)
    #             .values(parent_id=event_id, **patch.dict())
    #             .returning(EventPatch)
    #             .options(joinedload(EventPatch.parent))
    #         )
    #         event_patch = await session.scalar(q)
    #         await session.commit()
    #         return ViewEventPatch.from_orm(event_patch)
    #
    # async def read_patches(self, event_id: int) -> list["ViewEventPatch"]:
    #     async with self._create_session() as session:
    #         q = select(EventPatch).where(EventPatch.parent_id == event_id).options(joinedload(EventPatch.parent))
    #         event_patches = await session.scalars(q)
    #         return [ViewEventPatch.from_orm(event_patch) for event_patch in event_patches]
    #
    # async def update_patch(self, patch_id: int, patch: "UpdateEventPatch") -> "ViewEventPatch":
    #     async with self._create_session() as session:
    #         q = (
    #             update(EventPatch)
    #             .where(EventPatch.id == patch_id)
    #             .values(**patch.dict(exclude_unset=True))
    #             .returning(EventPatch)
    #         )
    #         event_patch = await session.scalar(q)
    #         await session.commit()
    #         return ViewEventPatch.from_orm(event_patch)

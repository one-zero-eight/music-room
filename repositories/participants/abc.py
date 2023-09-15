from abc import ABCMeta, abstractmethod

from schemas import CreateParticipant, ViewParticipant


class AbstractParticipantRepository(metaclass=ABCMeta):
    # ------------------- CRUD ------------------- #
    @abstractmethod
    async def create(self, event: "CreateParticipant") -> "ViewParticipant":
        ...

    # @abstractmethod
    # async def read(self, event_id: int) -> "ViewEvent":
    #     ...
    #
    # @abstractmethod
    # async def update(self, event_id: int, event: "UpdateEvent") -> "ViewEvent":
    #     ...
    #
    # @abstractmethod
    # async def delete(self, event_id: int) -> None:
    #     ...
    #
    # # ^^^^^^^^^^^^^^^^^ CRUD ^^^^^^^^^^^^^^^^^ #
    #
    # # ------------------- PATCHES ------------------- #
    # @abstractmethod
    # async def add_patch(self, event_id: int, patch: "AddEventPatch") -> "ViewEventPatch":
    #     ...
    #
    # @abstractmethod
    # async def read_patches(self, event_id: int) -> list["ViewEventPatch"]:
    #     ...
    #
    # @abstractmethod
    # async def update_patch(self, patch_id: int, patch: "UpdateEventPatch") -> "ViewEventPatch":
    #     ...

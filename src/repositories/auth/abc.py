from abc import ABCMeta, abstractmethod


class AbstractAuthRepository(metaclass=ABCMeta):
    @abstractmethod
    async def is_user_registered(self, email: str, telegram_id: str) -> bool:
        ...

    @abstractmethod
    async def save_code(self, email: str, code: str) -> None:
        ...

    @abstractmethod
    async def is_code_valid(self, email: str, code: str) -> bool:
        ...

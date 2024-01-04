from typing import TypeVar, Union, Callable, ClassVar, Hashable, TypeAlias, Annotated

from fastapi import Depends

T = TypeVar("T")

CallableOrValue = Union[Callable[[], T], T]


class Dependencies:
    providers: ClassVar[dict[type, CallableOrValue]] = {}

    @classmethod
    def register_provider(cls, key: type[T] | Hashable, provider: CallableOrValue):
        cls.providers[key] = provider

    @classmethod
    def get(cls, key: type[T] | Hashable) -> T:
        """
        Get shared dependency by key (f - fetch)
        """
        if key not in cls.providers:
            if isinstance(key, type):
                # try by classname
                key = key.__name__

                if key not in cls.providers:
                    raise KeyError(f"Provider for {key} is not registered")

            elif isinstance(key, str):
                # try by classname
                for cls_key in cls.providers.keys():
                    if cls_key.__name__ == key:
                        key = cls_key
                        break
                else:
                    raise KeyError(f"Provider for {key} is not registered")

        provider = cls.providers[key]

        if callable(provider):
            return provider()
        else:
            return provider


from src.api.auth.dependencies import verify_request  # noqa: E402
from src.schemas.auth import VerificationResult  # noqa: E402

VerifiedDep: TypeAlias = Annotated[VerificationResult, Depends(verify_request)]

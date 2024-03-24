__all__ = ["VerifiedDep", "SucceedVerificationResult"]

from typing import TypeAlias, Annotated, Literal

from fastapi import Depends

from src.api.auth.dependencies import verify_request
from src.schemas.auth import VerificationResult, VerificationSource


class SucceedVerificationResult(VerificationResult):
    success: Literal[True] = True
    user_id: int  # not optional
    source: VerificationSource


VerifiedDep: TypeAlias = Annotated[SucceedVerificationResult, Depends(verify_request)]

__all__ = ["VerificationResult", "AuthResult", "VerificationSource"]

from enum import StrEnum
from typing import Optional

from pydantic import BaseModel


class VerificationSource(StrEnum):
    USER = "user"
    WEBAPP = "webapp"
    BOT = "bot"


class VerificationResult(BaseModel):
    success: bool
    user_id: Optional[int] = None
    source: Optional[VerificationSource] = None


class AuthResult(BaseModel):
    success: bool
    token: Optional[str] = None

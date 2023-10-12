__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="/participants", tags=["Participants"])

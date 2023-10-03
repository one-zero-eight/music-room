from fastapi import FastAPI

from api.dependencies import Dependencies
from api.routers import routers
from config import settings
from repositories.auth.repository import SqlAuthRepository
from repositories.bookings.repository import SqlBookingRepository
from repositories.participants.repository import SqlParticipantRepository
from storage.sql import SQLAlchemyStorage

app = FastAPI()


async def setup_repositories():
    # ------------------- Repositories Dependencies -------------------
    storage = SQLAlchemyStorage.from_url(settings.DB_URL)
    participant_repository = SqlParticipantRepository(storage)
    booking_repository = SqlBookingRepository(storage)
    auth_repository = SqlAuthRepository(storage)
    Dependencies.set_storage(storage)
    Dependencies.set_participant_repository(participant_repository)
    Dependencies.set_booking_repository(booking_repository)
    Dependencies.set_auth_repository(auth_repository)

    # await storage.drop_all()
    # await storage.create_all()


@app.on_event("startup")
async def startup_event():
    await setup_repositories()


for router in routers:
    app.include_router(router)

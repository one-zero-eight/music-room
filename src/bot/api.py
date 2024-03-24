__all__ = ["api_client", "InNoHassleMusicRoomAPI", "UserStatus"]

import datetime
from enum import StrEnum
from typing import Any

import httpx

from src.config import bot_settings


class UserStatus(StrEnum):
    FREE = "free"
    MIDDLE = "middle"
    SENIOR = "senior"
    LORD = "lord"


# noinspection PyMethodMayBeStatic
class InNoHassleMusicRoomAPI:
    api_root_path: str

    def __init__(self, api_url: str):
        self.api_root_path = api_url

    def _create_client(self, /, telegram_id: int | None = None) -> httpx.AsyncClient:
        if telegram_id is not None:
            auth_header = {"Authorization": f"Bearer {telegram_id}:{bot_settings.bot_token.get_secret_value()}"}

        else:
            auth_header = {"Authorization": f"Bearer {bot_settings.bot_token.get_secret_value()}"}

        client = httpx.AsyncClient(headers=auth_header, base_url=self.api_root_path)
        return client

    async def start_registration(self, telegram_id: int) -> tuple[bool | None, Any]:
        params = {"telegram_id": telegram_id}
        async with self._create_client(telegram_id=telegram_id) as client:
            response = await client.post("/auth/registration", params=params)
            if response.status_code == 400:
                return None, "A user did not connect telegram to the account."
            if response.status_code == 409:
                return False, "A user with the provided telegram is already registered."
            if response.status_code == 200:
                return True, "A user has been successfully registered."
            raise RuntimeError("Unexpected response status")

    async def is_user_exists(self, telegram_id: int) -> bool:
        params = {"telegram_id": telegram_id}
        async with self._create_client() as client:
            response = await client.get("/auth/is_user_exists", params=params)
            return response.json()

    async def get_user_id(self, telegram_id: int) -> int | None:
        params = {"telegram_id": telegram_id}
        async with self._create_client() as client:
            response = await client.get("/users/user_id", params=params)
            if response.status_code == 200:
                return response.json()

    async def get_me(self, telegram_id: int) -> dict | None:
        async with self._create_client(telegram_id=telegram_id) as client:
            response = await client.get("/users/me")
            if response.status_code == 200:
                return response.json()

    async def fill_profile(self, telegram_id: int, name: str, alias: str) -> tuple[bool, Any]:
        body = {"name": name, "alias": alias}
        async with self._create_client(telegram_id=telegram_id) as client:
            response = await client.post("/users/me/fill_profile", json=body)
            if response.status_code == 200:
                return True, None
            else:
                return False, "There was an error during filling profile."

    async def get_remaining_daily_hours(self, telegram_id: int, date: str) -> float | None:
        params = {"date": date}
        async with self._create_client(telegram_id=telegram_id) as client:
            response = await client.get("/users/me/remaining_daily_hours", params=params)
            if response.status_code != 200:
                return None
            remaining_daily_hours = float(response.text)
        return remaining_daily_hours

    async def get_remaining_weekly_hours(self, telegram_id: int, date: str) -> float | None:
        params = {"date": date}
        async with self._create_client(telegram_id=telegram_id) as client:
            response = await client.get("/users/me/remaining_weekly_hours", params=params)
            if response.status_code != 200:
                return None
            remaining_weekly_hours = float(response.text)
        return remaining_weekly_hours

    async def get_daily_bookings(self, date: str | None) -> tuple[bool, Any]:
        params = {"date": date if date else datetime.date.today().isoformat()}
        async with self._create_client() as client:
            response = await client.get("/bookings/daily_bookings", params=params)
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, None

    async def book(
        self,
        telegram_id: int,
        date: datetime.date,
        time_start: datetime.time,
        time_end: datetime.time,
    ) -> tuple[bool, Any]:
        params = {
            "time_start": datetime.datetime.combine(date, time_start).isoformat(),
            "time_end": datetime.datetime.combine(date, time_end).isoformat(),
        }
        async with self._create_client(telegram_id=telegram_id) as client:
            response = await client.post("/bookings/", json=params)
            if response.status_code == 200:
                return True, None
            else:
                return False, response.json().get("detail")

    async def get_user_bookings(self, telegram_id: int) -> list[dict] | None:
        async with self._create_client(telegram_id=telegram_id) as client:
            response = await client.get("/bookings/my_bookings")
            if response.status_code == 200:
                return response.json()

    async def delete_booking(self, booking_id: int, telegram_id: int) -> bool:
        async with self._create_client(telegram_id=telegram_id) as client:
            response = await client.delete(f"/bookings/{booking_id}")
            return True if response.status_code == 200 else False

    async def get_image_schedule(self, start_of_week: datetime.date) -> bytes | None:
        params = {"start_of_week": start_of_week.isoformat()}
        async with self._create_client() as client:
            response = await client.get("/bookings/form_schedule", params=params)
            if response.status_code == 200:
                return response.read()

    async def export_users(self, telegram_id: int) -> tuple[bytes, str]:
        async with self._create_client(telegram_id=telegram_id) as client:
            response = await client.get("/users/export")
            if response.status_code == 200:
                bytes_ = response.read()
                filename = response.headers["Content-Disposition"].split("filename=")[1]
                return bytes_, filename


api_client: InNoHassleMusicRoomAPI = InNoHassleMusicRoomAPI(bot_settings.api_url)

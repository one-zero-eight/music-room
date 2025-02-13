import datetime

import httpx
from authlib.jose import JsonWebKey, KeySet
from pydantic import BaseModel

from src.config import settings


class UserInfoFromSSO(BaseModel):
    email: str
    name: str | None
    issued_at: datetime.datetime | None


class TelegramWidgetData(BaseModel):
    hash: str
    id: int
    auth_date: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None


class UserSchema(BaseModel):
    innopolis_sso: UserInfoFromSSO | None
    telegram: TelegramWidgetData | None = None
    # innohassle_admin: bool = False


class InNoHassleAcounts:
    api_url: str
    api_jwt_token: str
    PUBLIC_KID = "public"
    key_set: KeySet

    def __init__(self, api_url: str, api_jwt_token: str):
        self.api_url = api_url
        self.api_jwt_token = api_jwt_token

    async def update_key_set(self):
        self.key_set = await self.get_key_set()

    async def get_key_set(self) -> KeySet:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_url}/.well-known/jwks.json")
            response.raise_for_status()
            jwks_json = response.json()
            return JsonWebKey.import_key_set(jwks_json)

    def get_public_key(self) -> JsonWebKey:
        return self.key_set.find_by_kid(self.PUBLIC_KID)

    def get_authorized_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(headers={"Authorization": f"Bearer {self.api_jwt_token}"})

    async def get_user_by_telegram_id(self, telegram_id: int) -> UserSchema | None:
        async with self.get_authorized_client() as client:
            response = await client.get(f"{self.api_url}/users/by-telegram-id/{telegram_id}")
            try:
                response.raise_for_status()
                return UserSchema.model_validate(response.json())
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None
                raise e

    async def get_user_by_innohassle_id(self, innohassle_id: str) -> UserSchema | None:
        async with self.get_authorized_client() as client:
            response = await client.get(f"{self.api_url}/users/by-id/{innohassle_id}")
            try:
                response.raise_for_status()
                return UserSchema.model_validate(response.json())
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None
                raise e


innohassle_accounts: InNoHassleAcounts = InNoHassleAcounts(
    api_url=settings.accounts.api_url, api_jwt_token=settings.accounts.api_jwt_token.get_secret_value()
)

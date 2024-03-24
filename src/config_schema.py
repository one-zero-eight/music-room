from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, SecretStr, ConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    STAGING = "staging"


class BotSettings(BaseModel):
    environment: Environment = Environment.DEVELOPMENT
    bot_token: SecretStr = Field(..., description="Bot token from @BotFather")
    api_url: str
    redis_url: SecretStr | None = None


class ApiSettings(BaseModel):
    app_root_path: str = Field("", description='Prefix for the API path (e.g. "/api/v0")')
    db_url: str = Field(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
        example="postgresql+asyncpg://user:password@localhost:5432/db_name",
    )
    # Authorization
    bot_token: str = Field(
        ...,
        example="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        description="Bot token from @BotFather",
    )
    jwt_private_key: SecretStr = Field(
        ...,
        description="Private key for JWT. Use 'openssl genrsa -out private.pem 2048' to generate keys",
    )

    jwt_public_key: str = Field(
        ...,
        description="Public key for JWT. Use 'openssl rsa -in private.pem -pubout -out public.pem' to generate keys",
    )
    # SMTP server config
    smtp_server: str = Field(..., example="smtp.gmail.com")
    smtp_port: int = Field(587)
    smtp_username: str = Field(..., example="some-username@gmail.com")
    smtp_password: str = Field(..., example="xxxxxxxx")
    crypto_password: bytes = Field(
        ...,
        example=b"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        description="Run 'openssl rand -hex 32' to generate key",
    )
    crypto_salt: bytes = Field(..., example=b"xxxxxxxxxxxxxxxx")
    api_key: str = Field(
        ..., example="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", description="API key for the Music Room API"
    )


class Settings(BaseModel):
    model_config = ConfigDict(json_schema_extra={"title": "Settings"}, extra="ignore")
    api_settings: ApiSettings | None = None
    bot_settings: BotSettings | None = None

    @classmethod
    def from_yaml(cls, path: Path) -> "Settings":
        with open(path, "r", encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f)

        return cls.model_validate(yaml_config)

    @classmethod
    def save_schema(cls, path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            schema = {
                "$schema": "https://json-schema.org/draft-07/schema",
                **cls.model_json_schema(),
            }
            yaml.dump(schema, f, sort_keys=False)

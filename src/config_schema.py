from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from src.schemas.smtp import MailingTemplate


class Settings(BaseModel):
    APP_ROOT_PATH: str = Field("", description='Prefix for the API path (e.g. "/api/v0")')

    DB_URL: str = Field(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
        example="postgresql+asyncpg://user:password@localhost:5432/db_name",
    )

    # SMTP server config
    SMTP_SERVER: str = Field(..., example="smtp.gmail.com")
    SMTP_PORT: int = Field(587)
    SMTP_USERNAME: str = Field(..., example="some-username@gmail.com")
    SMTP_PASSWORD: str = Field(..., example="xxxxxxxx")
    REGISTRATION_MESSAGE_TEMPLATE: MailingTemplate = Field(
        default=MailingTemplate(
            subject="Registration in InNoHassle-MusicRoom",
            file="auth-code.jinja2",
        ),
        description="Mailing template settings",
    )
    JINJA2_TEMPLATES_DIR: Path = Field(default=Path("templates"), description="Path to the templates directory")

    CRYPTO_PASSWORD: bytes = Field(
        ...,
        example=b"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        description="Run 'openssl rand -hex 32' to generate key",
    )
    CRYPTO_SALT: bytes = Field(..., example=b"xxxxxxxxxxxxxxxx")

    @classmethod
    def from_yaml(cls, path: Path) -> "Settings":
        with open(path, "r", encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f)

        return cls.model_validate(yaml_config)

    @classmethod
    def save_schema(cls, path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                **cls.model_json_schema(),
            }
            yaml.dump(schema, f, sort_keys=False)

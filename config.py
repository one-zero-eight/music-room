from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.local", env_file_encoding="utf-8")

    DB_URL: str


settings = Settings(_env_file=".env.local", _env_file_encoding="utf-8")

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_URL: str

    # SMTP server config
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    CRYPTO_SECRET_KEY: bytes

    class Config:
        env_file = ".env.local"
        env_file_encoding = "utf-8"


settings = Settings()

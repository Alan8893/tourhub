from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    url: str = "postgresql+psycopg://tourhub:tourhub@localhost:5432/tourhub"


class RedisSettings(BaseSettings):
    url: str = "redis://localhost:6379/0"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_nested_delimiter="__",
    )

    app_name: str = "TourHub"
    environment: str = "dev"

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
    ]

    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()


settings = Settings()

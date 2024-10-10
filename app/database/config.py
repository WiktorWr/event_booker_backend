from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_NAME: str = "event_booker"
    DATABASE_USER: str = "event_booker"
    DATABASE_PASSWORD: str = "event_booker"
    DATABASE_HOST: str = "db"
    DATABASE_PORT: str = "5432"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

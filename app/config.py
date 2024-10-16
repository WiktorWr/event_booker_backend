from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Event Booker API"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

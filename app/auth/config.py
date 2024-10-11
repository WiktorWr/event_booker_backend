from pydantic_settings import BaseSettings, SettingsConfigDict


from passlib.context import CryptContext


class Settings(BaseSettings):
    PASSWORD_CONTEXT: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

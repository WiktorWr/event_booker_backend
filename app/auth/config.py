from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi.security import OAuth2PasswordBearer


from passlib.context import CryptContext


class Settings(BaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str = "secret"
    JWT_REFRESH_SECRET_KEY: str = "secret-two"
    AUTH_TOKEN_URL: str = "/auth/token"
    OAUTH2_SCHEME: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl=AUTH_TOKEN_URL)
    PASSWORD_CONTEXT: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

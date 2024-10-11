from pydantic import BaseModel, Field, field_validator
import re
from .enums import UserRole


USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9-_]+$")
PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)

INVALID_USERNAME_ERROR = (
    "Username can only contain letters, numbers, hyphens, and underscores."
)
INVALID_PASSWORD_ERROR = "Password must contain at least one lowercase character, one uppercase character, one digit, and one special symbol."


class UserBaseSchema(BaseModel):
    username: str = Field(min_length=4, max_length=20)
    role: UserRole

    @field_validator("username", mode="after")
    def validate_username(cls, username: str) -> str:
        if not USERNAME_PATTERN.match(username):
            raise ValueError(INVALID_USERNAME_ERROR)
        return username


class CreateUserParams(UserBaseSchema):
    password: str = Field(min_length=8)

    @field_validator("password", mode="after")
    def validate_password(cls, password: str) -> str:
        if not PASSWORD_PATTERN.match(password):
            raise ValueError(INVALID_PASSWORD_ERROR)
        return password


class RepresentUser(UserBaseSchema):
    id: int

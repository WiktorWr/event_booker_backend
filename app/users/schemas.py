from pydantic import BaseModel


class UserGetSchema(BaseModel):
    id: int

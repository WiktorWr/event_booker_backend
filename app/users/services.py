from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from .models import User
from .schemas import CreateUserParams
from .validators import validate_user_create
from app.auth.config import settings as auth_settings


@validate_user_create
def create_user(params: CreateUserParams, db: Session = Depends(get_db)) -> User:
    user = User(
        username=params.username,
        hashed_password=auth_settings.PASSWORD_CONTEXT.hash(params.password),
        role=params.role,
    )

    db.add(user)
    db.commit()

    return user

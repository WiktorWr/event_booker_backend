import factory  # type: ignore[import-untyped]
from app.users.models import User
from sqlalchemy.orm import Session
from app.users.enums import UserRole


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User

    id: int = factory.Sequence(lambda n: n + 1)
    username: str = factory.Faker("user_name")
    hashed_password: str = factory.Faker("password")
    role: UserRole = UserRole.ORGANIZER


def setup_factories(db: Session) -> None:
    UserFactory._meta.sqlalchemy_session = db

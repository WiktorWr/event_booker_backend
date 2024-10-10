import factory  # type: ignore[import-untyped]
from app.users.models import User
from sqlalchemy.orm import Session


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User

    id: int = factory.Sequence(lambda n: n + 1)


def setup_factories(db: Session) -> None:
    UserFactory._meta.sqlalchemy_session = db

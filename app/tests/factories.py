import factory  # type: ignore[import-untyped]
from app.users.models import User
from app.auth.models import RevokedToken
from sqlalchemy.orm import Session
from app.users.enums import UserRole
from app.events.models import Enrollment, Event
from datetime import datetime


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User

    id: int = factory.Sequence(lambda n: n + 1)
    username: str = factory.Faker("user_name")
    hashed_password: str = factory.Faker("password")
    role: UserRole = UserRole.ORGANIZER


class RevokedTokenFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = RevokedToken

    id: int = factory.Sequence(lambda n: n + 1)
    hash: str = factory.Faker("uuid4")
    revoked_at: str = factory.Faker("date_time")


class EventFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Event

    id: int = factory.Sequence(lambda n: n + 1)
    title: str = factory.Faker("sentence", nb_words=4)
    description: str = factory.Faker("paragraph", nb_sentences=3)
    price: int = factory.Faker("random_int", min=100, max=100_000_000)
    max_capacity: int = factory.Faker("random_int", min=10, max=100)
    event_date: datetime = factory.Faker("date_time")
    organizer: User = factory.SubFactory(UserFactory)


class EnrollmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Enrollment

    participant: User = factory.SubFactory(UserFactory)
    event: Event = factory.SubFactory(EventFactory)


def setup_factories(db: Session) -> None:
    UserFactory._meta.sqlalchemy_session = db
    RevokedTokenFactory._meta.sqlalchemy_session = db
    EventFactory._meta.sqlalchemy_session = db
    EnrollmentFactory._meta.sqlalchemy_session = db

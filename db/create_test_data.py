import random

import factory

from db import models
from db.engine import Session, session_scope

# Указать здесь file_id фото из вашего бота.
IMAGE = (
    "AgACAgIAAxkBAAINs2U9E2g1IK6F2v8IFeoyMSSlsn7PAAIP0TEbm2DpSX8qIhX6pvPDAQA"
    "DAgADeAADMAQ"
)


class BaseSQLAlchemyModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"


class TeamFactory(BaseSQLAlchemyModelFactory):
    class Meta:
        model = models.Team

    name = factory.Sequence(lambda n: f"team{n}")
    team_size = factory.Faker("pyint", min_value=5, max_value=10)


class UserFactory(BaseSQLAlchemyModelFactory):
    class Meta:
        model = models.User

    name = factory.Faker("name")
    role = factory.Iterator(("methodist", "counsellor", "kid"))
    language = factory.Iterator(("RU", "EN", "TT"))
    score = factory.Faker("pyint", min_value=0, max_value=100)
    group = factory.Faker("pyint", min_value=1, max_value=5)
    team = factory.SubFactory(TeamFactory)


class CategoryFactory(BaseSQLAlchemyModelFactory):
    class Meta:
        model = models.Category

    name = factory.Faker("word")


class AchievementFactory(BaseSQLAlchemyModelFactory):
    class Meta:
        model = models.Achievement

    name = factory.Faker("word")
    image = IMAGE
    description = factory.Faker("paragraph")
    instruction = factory.Faker("paragraph")
    artifact_type = factory.Iterator(("text", "image", "video"))
    achievement_type = factory.Iterator(("individual", "teamwork"))
    score = factory.Faker("pyint", min_value=0, max_value=100)
    price = factory.Faker("pyint", min_value=0, max_value=100)
    category = factory.SubFactory(CategoryFactory)


class AchievementStatusFactory(BaseSQLAlchemyModelFactory):
    class Meta:
        model = models.AchievementStatus

    user = factory.SubFactory(UserFactory)
    achievement = factory.SubFactory(AchievementFactory)
    status = factory.Iterator(
        ("pending", "pending_methodist", "approved", "rejected")
    )
    files_id = IMAGE, IMAGE
    message_text = factory.Faker("paragraph")
    created_at = factory.Faker("date_time")
    rejection_reason = factory.Faker("paragraph")
    team = factory.SubFactory(TeamFactory)


def create_users(max_number):
    teams = TeamFactory.create_batch(2)
    UserFactory.create_batch(max_number, team=factory.Iterator(teams))


def create_users_achievements(min_number, session):
    users = session.query(models.User).all()
    achievements = session.query(models.Achievement).all()
    for user in users:
        achievement = random.choice(achievements)
        AchievementStatusFactory.create_batch(
            min_number,
            user=user,
            team=user.team,
            achievement=achievement,
        )


def create_test_data():
    min_number = 1
    max_number = 5
    try:
        with session_scope() as session:
            create_users(max_number)
            AchievementFactory.create_batch(max_number)
            create_users_achievements(min_number, session)

    except Exception as error:
        print(f"{error}")


if __name__ == "__main__":
    create_test_data()

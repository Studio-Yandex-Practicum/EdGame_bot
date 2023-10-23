import factory

from db import models
from db.engine import session

# Указать здесь file_id фото из вашего бота.
IMAGE = (
    "AgACAgIAAxkBAAIMgGUqmZfZqdt88lziFbzptSZcRuAtAAKe0jEb4nZQSUzRlbmA"
    "C2RrAQADAgADcwADMAQ"
)


class BaseSQLAlchemyModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = session
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
    role = factory.Iterator(("methodist", "counselor", "kid"))
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


def create_test_data():
    max_number = 5
    try:
        AchievementStatusFactory.create_batch(max_number)

    except Exception as error:
        print(f"{error}")


if __name__ == "__main__":
    create_test_data()

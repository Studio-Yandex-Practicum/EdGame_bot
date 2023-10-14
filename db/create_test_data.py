import factory

from db import models
from db.engine import session

IMAGE = "AgACAgIAAxkBAAICRWUk24JzSwrQNimyH_Sc8W5DL44hAAK-zjEbdikpSUYKQGP_2OPLAQADAgADeAADMAQ"


class BaseSQLAlchemyModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = session
        sqlalchemy_session_persistence = "commit"


class TeamFactory(BaseSQLAlchemyModelFactory):
    class Meta:
        model = models.Team

    name = factory.Sequence(lambda n: f"team{n}")
    team_size = factory.Faker('pyint', min_value=5, max_value=10)


class UserFactory(BaseSQLAlchemyModelFactory):
    class Meta:
        model = models.User

    name = factory.Faker("name")
    role = factory.Iterator(("methodist", "councelor", "kid"))
    language = factory.Iterator(("RU", "EN", "TT"))
    score = factory.Faker('pyint', min_value=0, max_value=100)
    group = factory.Faker('pyint', min_value=1, max_value=5)
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
    score = factory.Faker('pyint', min_value=0, max_value=100)
    price = factory.Faker('pyint', min_value=0, max_value=100)
    category = factory.SubFactory(CategoryFactory)


from engine import engine
from faker import Faker
from models import Achievement, AchievementStatus, User
from PIL import Image, ImageDraw
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import cast
from sqlalchemy.types import LargeBinary

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_test_data():
    """Генерирует фейковые данные."""
    fake = Faker()

    with SessionLocal() as session:
        # Генерируем тестовых пользователей
        # for _ in range(10):
        #     user = User(
        #         name=fake.name(),
        #         role=fake.random_element(["methodist", "counselor", "kid"]),
        #         language=fake.random_element(["ru", "en", "tt"]),
        #         score=fake.random_int(min=0, max=100),
        #     )
        #     session.add(user)

        # # Генерируем тестовые достижения
        # for _ in range(20):
        #     # Создаем случайное изображение
        #     image = Image.new("RGB", (100, 100))
        #     draw = ImageDraw.Draw(image)
        #     draw.rectangle([(0, 0), (100, 100)], fill=(255, 0, 0))
        #     image_byte_array = io.BytesIO()
        #     image.save(image_byte_array, format="PNG")
        #     image_data = image_byte_array.getvalue()

        #     achievement = Achievement(
        #         name=fake.word(),
        #         image=cast(
        #             image_data, LargeBinary
        #         ),  # Важно: преобразовываем в LargeBinary
        #         description=fake.text(max_nb_chars=255),
        #         instruction=fake.text(max_nb_chars=255),
        #         artifact_type=fake.random_element(["text", "image", "video"]),
        #         achievement_type=fake.random_element(["individual", "teamwork"]),
        #         score=fake.random_int(min=0, max=100),
        #         price=fake.random_int(min=0, max=100),
        #     )
        #     session.add(achievement)

        # Генерируем тестовые статусы достижений
        for user in session.query(User).all():
            for achievement in session.query(Achievement).all():
                achievement_status = AchievementStatus(
                    user_id=user.id,
                    achievement_id=achievement.id,
                    status=fake.random_element(["pending", "approved", "rejected"]),
                    created_at=fake.date_time(),
                    rejection_reason=fake.sentence(),
                )
                session.add(achievement_status)

        session.commit()


if __name__ == "__main__":
    create_test_data()

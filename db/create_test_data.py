import io
import random

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

import io
import random

from engine import engine
from faker import Faker
from models import Achievement, AchievementStatus, User
from PIL import Image, ImageDraw
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def generate_fake_image_data():
    """Генерирует фейковые изображения."""
    width = 100
    height = 100
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    image = Image.new("RGB", (width, height), color)
    draw = ImageDraw.Draw(image)
    for _ in range(1000):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        draw.point((x, y), fill=color)

    image_data = io.BytesIO()
    image.save(image_data, format="JPEG")
    image_data.seek(0)
    image_bytes = image_data.getvalue()
    image_data.close()

    return image_bytes


def create_test_data():
    """Генерирует фейковые данные."""
    fake = Faker()

    with SessionLocal() as session:
        # Генерируем тестовых пользователей
        # for _ in range(10):
        #     user = User(
        #         name=fake.name(),
        #         role=fake.random_element(["methodist", "counselor", "kid"]),
        #         login=fake.user_name(),
        #         password=fake.password(),
        #         language=fake.random_element(["ru", "en", "tt"]),
        #         score=fake.random_int(min=0, max=100),
        #     )
        #     session.add(user)

        # # Генерируем тестовые достижения
        # for _ in range(20):
        #     achievement = Achievement(
        #         name=fake.word(),
        #         image=generate_fake_image_data(),
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

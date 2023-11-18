from aiogram import types
from sqlalchemy.orm import Session

from db.engine import session
from db.models import Achievement, AchievementStatus, Category, User


def get_user_name(session: Session, user_id: int) -> str:
    user = session.query(User).filter(User.id == user_id).first()
    return user.name


def get_all_children(session: Session):
    return session.query(User).filter(User.role == "kid").all()


def get_all_children_from_group(session: Session, group_id: int):
    return (
        session.query(User)
        .filter(User.group == group_id, User.role == "kid")
        .all()
    )


def get_all_child_achievements(session: Session, child_id):
    return (
        session.query(AchievementStatus)
        .filter(
            AchievementStatus.user_id == child_id,
            AchievementStatus.status == "pending",
        )
        .all()
    )


def get_child_by_name_and_group(session: Session, name, group):
    return (
        session.query(User)
        .filter(User.name == name, User.group == group, User.role == "kid")
        .first()
    )


def get_achievement_name(session: Session, achievement_id: int) -> str:
    achievement = (
        session.query(Achievement)
        .filter(Achievement.id == achievement_id)
        .first()
    )
    return achievement.name


def get_achievement_description(session: Session, achievement_id: int) -> str:
    achievement = (
        session.query(Achievement)
        .filter(Achievement.id == achievement_id)
        .first()
    )
    return achievement.description


def get_achievement_instruction(session: Session, achievement_id: int) -> str:
    achievement = (
        session.query(Achievement)
        .filter(Achievement.id == achievement_id)
        .first()
    )
    return achievement.instruction


def get_achievement_file_id(session: Session, achievement_id: int) -> bytes:
    achievement = (
        session.query(AchievementStatus)
        .filter(AchievementStatus.achievement_id == achievement_id)
        .first()
    )
    return achievement.files_id


def get_achievement_file_type(session: Session, achievement_id: int) -> bytes:
    achievement = (
        session.query(Achievement)
        .filter(Achievement.id == achievement_id)
        .first()
    )

    return achievement.artifact_type


def get_message_text(session: Session, id: int):
    achievement_status = (
        session.query(AchievementStatus)
        .filter(AchievementStatus.id == id)
        .first()
    )
    return achievement_status.message_text


def get_achievements_by_name(session: Session, achievement_name: str):
    """Возвращает все запросы на проверку одного задания."""
    achievements = (
        session.query(Achievement)
        .join(AchievementStatus)
        .filter(
            Achievement.name == achievement_name,
            AchievementStatus.status == "pending",
        )
        .first()
    )
    return achievements.id


def get_achievement_status_by_id(session: Session, achievement_id):
    return (
        session.query(AchievementStatus)
        .filter(AchievementStatus.achievement_id == achievement_id)
        .all()
    )


def get_achievement_status(session: Session, achievement_id: int):
    return (
        session.query(AchievementStatus)
        .filter_by(achievement_id=achievement_id)
        .all()
    )


def change_achievement_status_by_id(
    session: Session, id: int, new_status: str
) -> bool:
    """Получает AchievementStatus по его id и изменяет статус задания."""
    if achievement_status := (
        session.query(AchievementStatus)
        .filter(AchievementStatus.id == id)
        .first()
    ):
        achievement_status.status = new_status
        session.commit()
        return True
    return False


def save_rejection_reason_in_db(id: int, message_text: str):
    """Сохраняет причину отказа принять задание."""
    user_achievement = (
        session.query(AchievementStatus)
        .filter(AchievementStatus.id == id)
        .first()
    )
    user_achievement.rejection_reason = message_text
    session.commit()
    return True


async def send_task(
    message: types.Message,
    file_type,
    file_id,
    caption,
    message_text,
    inline_keyboard,
):
    if file_type == "image":
        await message.answer_photo(
            photo=file_id[0], caption=caption, reply_markup=inline_keyboard
        )
    elif file_type == "video":
        await message.answer_video(
            video=file_id[0], caption=caption, reply_markup=inline_keyboard
        )
    elif file_type == "text":
        await message.answer(
            f"{caption}\n\n{message_text}", reply_markup=inline_keyboard
        )
    else:
        await message.answer("Не удалось получить файл по id")


def get_all_categories(session: Session):
    return session.query(Category).all()


def get_achievement_by_category_id(session: Session, category_id):
    achievement_by_category = (
        session.query(Achievement)
        .filter(Achievement.category_id == category_id)
        .all()
    )
    available_achievements_list = []
    for available_achievement in achievement_by_category:
        available_achievements_list.append((available_achievement))
    return available_achievements_list

import os

import requests
from sqlalchemy.orm import Session

from db.models import Achievement, AchievementStatus, User


def get_user_name(session: Session, user_id: int) -> str:
    user = session.query(User).filter(User.id == user_id).first()
    return user.name if user else "Unknown User"


def get_achievement_name(session: Session, achievement_id: int) -> str:
    achievement = (
        session.query(Achievement)
        .filter(Achievement.id == achievement_id)
        .first()
    )
    return achievement.name if achievement else "Unknown Achievement"


def get_achievement_description(session: Session, achievement_id: int) -> str:
    achievement = (
        session.query(Achievement)
        .filter(Achievement.id == achievement_id)
        .first()
    )
    return achievement.description if achievement else "Unknown Achievement"


def get_achievement_instruction(session: Session, achievement_id: int) -> str:
    achievement = (
        session.query(Achievement)
        .filter(Achievement.id == achievement_id)
        .first()
    )
    return achievement.instruction if achievement else "Unknown Achievement"


def get_achievement_file_id(session: Session, achievement_id: int) -> bytes:
    achievement = (
        session.query(AchievementStatus)
        .filter(AchievementStatus.achievement_id == achievement_id)
        .first()
    )
    return achievement.files_id if achievement else "Unknown File"


def get_achievement_file_type(session: Session, achievement_id: int) -> bytes:
    achievement = (
        session.query(Achievement)
        .filter(Achievement.id == achievement_id)
        .first()
    )

    return achievement.artifact_type if achievement else "Unknown Achievement"


def get_message_text(session: Session, id: int):
    achievement_status = (
        session.query(AchievementStatus)
        .filter(AchievementStatus.id == id)
        .first()
    )
    return (
        achievement_status.message_text
        if achievement_status
        else "Unknown Message"
    )


def get_message_text(session: Session, id: int):
    achievement_status = (
        session.query(AchievementStatus)
        .filter(AchievementStatus.id == id)
        .first()
    )
    return (
        achievement_status.message_text
        if achievement_status
        else "Unknown Message"
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


def save_rejection_reason_in_db(session: Session, id: int, message_text: str):
    """Сохраняет причину отказа принять задание."""
    user_achievement = (
        session.query(AchievementStatus)
        .filter(AchievementStatus.id == id)
        .first()
    )
    user_achievement.rejection_reason = message_text
    session.commit()
    return True


async def send_achievement_file(
    message,
    child,
    achievement_name,
    achievement_description,
    achievement_instruction,
    achievement_file_id,
    achievement_file_type,
    inline_keyboard,
):
    "Отправляет задание на проверку вожатому с файлом из БД."
    if achievement_file_type in [
        "image"
    ]:  # TODO: надо переписать через switch/case
        await message.answer_photo(
            photo=achievement_file_id[0],
            caption=(
                f"Задание на проверку от {child.name}:\n{achievement_name} - \
            {achievement_description} - {achievement_instruction}"
            ),
            reply_markup=inline_keyboard,
        )
    elif achievement_file_type == "video":
        await message.answer_video(
            video=achievement_file_id[0],
            caption=(
                f"Задание на проверку от {child.name}:\n{achievement_name} - \
                {achievement_description} - {achievement_instruction}"
            ),
            reply_markup=inline_keyboard,
        )
    elif achievement_file_type == "text":
        await message.answer(
            f"Задание на проверку от {child.name}:\n{achievement_name} - \
                {achievement_description} - {achievement_instruction}",
            reply_markup=inline_keyboard,
        )
    else:
        await message.answer("Не удалось получить файл по id")

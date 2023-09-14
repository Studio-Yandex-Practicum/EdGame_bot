import time
import logging
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from db.engine import session
from db.models import Achievement, AchievementStatus, User

logger = logging.getLogger(__name__)


def register_user(data):
    user = User(
        id=data['id'], name=data['name'], role="kid",
        language=data['language'], score=0,
        group=data['group']
    )
    session.add(user)
    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()  # откатываем session.add(user)
        return False


def select_user(user_id) -> User:
    """Получаем пользователя по id."""
    user = session.query(User).filter(User.id == user_id).first()
    return user


def get_users_by_role(role: str):
    """Получаем пользователей по статусу."""
    users = session.query(User).filter(User.role == role).all()
    return users


def set_user_param(
    user: User,
    name: str = None,
    role: str = None,
    language: str = None,
    score: int = None,
):
    """Сеттер для обновления свойств объекта User."""
    if name:
        user.name = name
    if role:
        user.role = role
    if language:
        user.language = language
    if score:
        user.score = score
    try:
        session.commit()
        logger.info('Пользователь обновлен')
    except IntegrityError as err:
        logger.error(f'Ошибка при обновлении пользователя: {err}')
        session.rollback()


def user_achievements(user_id):
    """
    Вставляем id текущего пользователя и получаем список кортежей, где у нас
    имеется объект ачивки (вынимаем необходимые для бота данные), статус
    проверки и причину отказа, если та имеется.
    """
    user_achievements = session.query(AchievementStatus).filter(
        AchievementStatus.user_id == user_id
    )
    achievement_list = []
    for user_achievement in user_achievements:
        status = user_achievement.status
        rejection_reason = user_achievement.rejection_reason
        achievement = (
            session.query(Achievement)
            .filter(Achievement.id == user_achievement.achievement_id)
            .first()
        )
        achievement_list.append((achievement, status, rejection_reason))
    return achievement_list


def available_achievements(user_id, user_score) -> list:
    """
    Присылаем id пользователя, получаем список доступных ему по количеству
    баллов ачивок, среди который нет находящихся в проверке или уже
    выполненных, из которых вынимаем нужные данные.
    """
    user_achievements = session.query(AchievementStatus).filter(
        AchievementStatus.user_id == user_id,
        AchievementStatus.status != "rejected",
    )
    nonavailable_achievement_list = []
    for user_achievement in user_achievements:
        nonavailable_achievement_list.append((user_achievement.achievement_id))
    available_achievements = session.query(Achievement).filter(
        Achievement.id.not_in(nonavailable_achievement_list),
        Achievement.price <= user_score,
    )
    available_achievements_list = []
    for available_achievement in available_achievements:
        available_achievements_list.append((available_achievement))
    return available_achievements_list


def get_achievement(achievement_id: int = None,
                    name: str = None) -> Achievement:
    '''Достаем ачивку из базы по ее id.'''
    achievement = (
        session.query(
            Achievement).filter(
            Achievement.id == achievement_id if achievement_id
            else Achievement.name == name
        ).first())
    return achievement if achievement else "Unknown Achievement"


def get_all_achievements(status: str = None):
    """Возвращает все ачивки из базы."""
    achievements = session.query(Achievement).all()
    if status:
        achievement_statuses = (
            session.query(AchievementStatus)
            .filter(AchievementStatus.status == status)
            .all()
        )
        achievements = []
        for achievement_status in achievement_statuses:
            user = select_user(achievement_status.user_id)
            task = get_achievement(achievement_status.achievement_id)
            achievements.append((user, task, achievement_status))
    return achievements


def set_achievement_param(achievement_id: int, name: str = None,
                          description: str = None, instruction: str = None,
                          score: int = None, price: int = None,
                          artifact_type: str = None, image: str = None,
                          achievement_type: str = None):
    '''Сеттер для обновления свойств объекта Achievement.'''
    achievement = get_achievement(achievement_id)
    if name:
        achievement.name = name
    if description:
        achievement.description = description
    if instruction:
        achievement.instruction = instruction
    if image:
        achievement.image = image
    if score:
        achievement.score = score
    if price:
        achievement.price = price
    if artifact_type:
        achievement.artifact_type = artifact_type
    if achievement_type:
        achievement.achievement_type = achievement_type
    try:
        session.commit()
        logger.info('Ачивка обновлена')
        return True
    except IntegrityError as err:
        logger.error(f'Ошибка при обновлении ачивки: {err}')
        session.rollback()
        return False


def send_task(user_id, achievement_id, files_id, message_text):
    """
    На вход: user_id текущего юзера, которого мы получили при старте бота в
    select_user(), achievement_id, полученный из ачивки, на кнопку которой
    юзер нажмёт, files_id, список, который будет состоять из id
    отправленных юзером артефактов, message_text, сообщение, которое может
    прислать юзер вместе с заданием. Значения files_id и message_text могут
    быть None. На выходе получаем новую запись AchievementStatus.
    """
    task = AchievementStatus(
        user_id=user_id,
        achievement_id=achievement_id,
        files_id=files_id,
        message_text=message_text,
        status="pending",
        created_at=datetime.fromtimestamp(time.time()),
    )

    session.add(task)

    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def change_language(user_id, language):
    # На вход: user_id текущего юзера, которого мы получили при старте бота в
    # select_user(), язык на который хотим сменить.
    session.query(User).filter(User.id == user_id).update(
        {"language": language}
    )

    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def approve_task(user_achievement_id):
    # На вход: user_achievement_id проверяемой ачивки. Для кнопки "одобрить"
    # Переводит ачивку в статус одобренно и начисляет её баллы пользователю
    user_achievement = (
        session.query(AchievementStatus)
        .filter(AchievementStatus.id == user_achievement_id)
        .first()
    )
    user_achievement.status = "approved"
    achievement = (
        session.query(Achievement)
        .filter(Achievement.id == user_achievement.achievement_id)
        .first()
    )
    user = (
        session.query(User).filter(User.id == user_achievement.user_id).first()
    )
    user.score += achievement.score
    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def reject_task(user_achievement_id):
    # На вход: user_achievement_id проверяемой ачивки и причину отказа.
    # Для кнопки "отказать".
    user_achievement = (
        session.query(AchievementStatus)
        .filter(AchievementStatus.id == user_achievement_id)
        .first()
    )
    user_achievement.status = "rejected"
    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def send_to_methdist(user_achievement_id):
    # На вход: user_achievement_id проверяемой ачивки.
    # Для кнопки "отправить методисту".
    user_achievement = (
        session.query(AchievementStatus)
        .filter(AchievementStatus.id == user_achievement_id)
        .first()
    )
    user_achievement.status = "pending_methodist"
    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def create_achievement(data: dict):
    """Метод для создания новой ачивки в базе."""
    new_achievement = Achievement(
        name=data.get('name', 'test'),
        image=data.get('image'),
        description=data.get('description', 'test_desc'),
        instruction=data.get('instruction', 'test_inst'),
        price=data.get('price', 0),
        score=data.get('score', 0),
        achievement_type=data.get('achievement_type', 'individual'),
        artifact_type=data.get('artifact_type', 'text')
    )
    session.add(new_achievement)
    try:
        session.commit()
        logger.info('Ачивка добавлена')
        return True
    except IntegrityError as err:
        session.rollback()  # откатываем session.add(user)
        logger.error(f'Ошибка при сохранении ачивки: {err}')
        return False


def get_user_achievement(user_achievement_id: int) -> AchievementStatus:
    '''Достаем ачивку из базы по ее id.'''
    user_achievement = (
        session.query(
            AchievementStatus).filter(
            AchievementStatus.id == user_achievement_id
        ).first())
    return user_achievement

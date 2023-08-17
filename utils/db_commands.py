import time
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from db.models import User, AchievementStatus, Achievement
from db.engine import session


def register_user(message):
    name = message.chat.first_name if message.chat.first_name else None
    user = User(
        id=int(message.chat.id), name=name, role="kid", language="RU", score=0
        )

    session.add(user)

    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()  # откатываем session.add(user)
        return False


def select_user(user_id):
    user = session.query(User).filter(User.id == user_id).first()
    return user


def user_achievements(user_id):
    # Вставляем id текущего пользователя и получаем список кортежей, где у нас
    # имеется объект ачивки (вынимаем необходимые для бота данные), статус
    # проверки и причину отказа, если та имеется.
    user_achievements = session.query(AchievementStatus).filter(
        AchievementStatus.user_id == user_id
        )
    achievement_list = []
    for user_achievement in user_achievements:
        status = user_achievement.status
        rejection_reason = user_achievement.rejection_reason
        achievement = session.query(Achievement).filter(
            Achievement.id == user_achievement.achievement_id).first()
        achievement_list.append((achievement, status, rejection_reason))
    return achievement_list


def available_achievements(user_id, user_score):
    # Присылаем id пользователя, получаем список доступных ему по количеству
    # баллов ачивок, среди который нет находящихся в проверке или уже
    # выполненных, из которых вынимаем нужные данные.
    user_achievements = session.query(AchievementStatus).filter(
        AchievementStatus.user_id == user_id,
        AchievementStatus.status != 'rejected'
        )
    nonavailable_achievement_list = []
    for user_achievement in user_achievements:
        nonavailable_achievement_list.append((user_achievement.achievement_id))
    available_achievements = session.query(Achievement).filter(
        Achievement.id.not_in(nonavailable_achievement_list),
        Achievement.price <= user_score
        )
    available_achievements_list = []
    for available_achievement in available_achievements:
        available_achievements_list.append((available_achievement))
    return available_achievements_list


def send_task(user_id, achievement_id, files_id, message_text):
    # На вход: user_id текущего юзера, которого мы получили при старте бота в
    # select_user(), achievement_id, полученный из ачивки, на кнопку которой
    # юзер нажмёт, files_id, список, который будет состоять из id
    # отправленных юзером артефактов, message_text, сообщение, которое может
    # прислать юзер вместе с заданием. Значения files_id и message_text могут
    # быть None. На выходе получаем новую запись AchievementStatus.
    task = AchievementStatus(
        user_id=user_id,
        achievement_id=achievement_id,
        files_id=files_id,
        message_text=message_text,
        status="pending",
        created_at=datetime.fromtimestamp(time.time())
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
        {'language': language}
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
    user_achievement = session.query(AchievementStatus).filter(
        AchievementStatus.id == user_achievement_id
        ).first()
    user_achievement.status = 'approved'
    achievement = session.query(Achievement).filter(
        Achievement.id == user_achievement.achievement_id
        ).first()
    user = session.query(User).filter(
        User.id == user_achievement.user_id
        ).first()
    user.score += achievement.score
    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def reject_task(user_achievement_id, rejection_reason):
    # На вход: user_achievement_id проверяемой ачивки и причину отказа.
    # Для кнопки "отказать".
    user_achievement = session.query(AchievementStatus).filter(
        AchievementStatus.id == user_achievement_id
        ).first()
    user_achievement.status = 'rejected'
    user_achievement.rejection_reason = rejection_reason
    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def send_to_methdist(user_achievement_id):
    # На вход: user_achievement_id проверяемой ачивки.
    # Для кнопки "отправить методисту".
    user_achievement = session.query(AchievementStatus).filter(
        AchievementStatus.id == user_achievement_id
        ).first()
    user_achievement.status = 'pending_methodist'
    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False

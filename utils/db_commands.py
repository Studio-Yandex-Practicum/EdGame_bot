import logging
import time
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from db.engine import session
from db.models import (
    Achievement,
    AchievementStatus,
    Category,
    Password,
    Team,
    User,
)

from .pass_gen import counsellor_pass, master_pass, methodist_pass

logger = logging.getLogger(__name__)


def register_user(data):
    user = User(
        id=data["id"],
        name=data["name"],
        role="kid",
        language=data["language"],
        score=0,
        group=data["group"],
    )
    session.add(user)
    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()  # откатываем session.add(user)
        return False


def check_password():
    password = session.query(Password).first()
    if password is None:
        password = Password(
            master_pass=master_pass,
            counsellor_pass=counsellor_pass,
            methodist_pass=methodist_pass,
        )
        session.add(password)
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


def is_user_in_db(user_id):
    """Проверяем наличие пользователя в базе данных."""
    return session.query(
        session.query(User).filter(User.id == user_id).exists()
    ).scalar()


def get_users_by_role(role: str):
    """Получаем пользователей по статусу."""
    users = session.query(User).filter(User.role == role).all()
    return users


def get_users_by_role_and_group(role: str, group: int):
    """Получаем пользователей по статусу и номеру отряда."""
    users = (
        session.query(User)
        .filter(User.role == role, User.group == group)
        .all()
    )
    return users


def set_user_param(
    user: User,
    name: str = None,
    language: str = None,
    score: int = None,
    team: Team = None,
    delete_team: bool = False,
    captain_of_team: int = None,
    leave_captain_pos: bool = False,
):
    """Сеттер для обновления свойств объекта User."""
    if name:
        user.name = name
    if language:
        user.language = language
    if score:
        user.score = score
    if team:
        user.team = team
    if delete_team:
        user.team = None
    if captain_of_team:
        user.captain_of_team_id = captain_of_team
    if leave_captain_pos:
        user.captain_of_team_id = None
    try:
        session.commit()
        logger.info("Пользователь обновлен")
    except IntegrityError as err:
        logger.error(f"Ошибка при обновлении пользователя: {err}")
        session.rollback()


def user_achievements(user_id):
    """
    Задания в кабинете ребенка.

    Вставляем id текущего пользователя и получаем список кортежей.
    В кортежах у нас имеется объект ачивки (вынимаем необходимые
    для бота данные), статус проверки и причину отказа, если та имеется.
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
    Функция для получения доступных ачивок.

    Присылаем id пользователя, получаем список доступных ему по количеству
    баллов ачивок, среди которых нет находящихся на проверке или уже
    выполненных. Из них вынимаем нужные данные.
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


def get_achievement(
    achievement_id: int = None, name: str = None
) -> Achievement:
    """Достаем ачивку из базы по ее id."""
    achievement = (
        session.query(Achievement)
        .filter(
            Achievement.id == achievement_id
            if achievement_id
            else Achievement.name == name
        )
        .first()
    )
    return achievement if achievement else "Unknown Achievement"


def get_all_achievements():
    """Возвращает все ачивки из базы."""
    achievements = session.query(Achievement).all()
    return achievements


def set_achievement_param(
    achievement_id: int,
    name: str = None,
    description: str = None,
    instruction: str = None,
    score: int = None,
    price: int = None,
    artifact_type: str = None,
    image: str = None,
    achievement_type: str = None,
    achievements_category: int = None,
):
    """Сеттер для обновления свойств объекта Achievement."""
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
    if achievements_category:
        achievement.category_id = achievements_category
    try:
        session.commit()
        logger.info("Ачивка обновлена")
        return True
    except IntegrityError as err:
        logger.error(f"Ошибка при обновлении ачивки: {err}")
        session.rollback()
        return False


def send_task(
    user: User, achievement: Achievement, files_id: list, message_text: str
) -> bool:
    """
    Сохраняет задание, отправленное на проверку.

    Функция для создания объекта AchievementStatus.
    На вход: user текущий юзер, которого мы получили при старте бота в
    select_user(), achievement, полученная ачивка, на кнопку которой
    юзер нажмёт, files_id, список, который будет состоять из id
    отправленных юзером артефактов, message_text, сообщение, которое может
    прислать юзер вместе с заданием. Значения files_id и message_text могут
    быть None. На выходе получаем новую запись AchievementStatus.
    """
    team = (
        user.captain_of_team_id
        if achievement.achievement_type == "teamwork"
        else None
    )
    task = AchievementStatus(
        user_id=user.id,
        achievement_id=achievement.id,
        files_id=files_id,
        message_text=message_text,
        status="pending",
        created_at=datetime.fromtimestamp(time.time()),
        team_id=team,
    )

    session.add(task)

    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def change_language(user_id, language):
    """
    Функция для обновления языка пользователя.

    На вход: user_id текущего юзера, которого мы получили при старте бота в
    select_user(), язык на который хотим сменить.
    """
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
    """
    Функция для изменения статуса ачивки (объект AchievementStatus).

    На вход: user_achievement_id проверяемой ачивки. Для кнопки "одобрить"
    Переводит ачивку в статус одобренно и начисляет её баллы пользователю.
    """
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

    team = (
        session.query(User)
        .filter(User.team_id == user_achievement.team_id)
        .all()
    )
    if achievement.achievement_type == "individual":
        user.score += achievement.score
    elif achievement.achievement_type == "teamwork":
        for user in team:
            user.score += achievement.score
    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def reject_task(user_achievement_id):
    """
    Функция для отклонения задания.

    На вход: user_achievement_id проверяемой ачивки и причину отказа.
    Для кнопки "отказать".
    """
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
    """
    Функция для передачи ачивки от вожатого методисту.

    На вход: user_achievement_id проверяемой ачивки.
    Для кнопки "отправить методисту".
    """
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
        name=data.get("name", "test"),
        image=data.get("image"),
        description=data.get("description", "test_desc"),
        instruction=data.get("instruction", "test_inst"),
        price=data.get("price", 0),
        score=data.get("score", 0),
        achievement_type=data.get("achievement_type", "individual"),
        artifact_type=data.get("artifact_type", "text"),
        category_id=data.get("category_id"),
    )
    session.add(new_achievement)
    try:
        session.commit()
        logger.info("Ачивка добавлена")
        return True
    except IntegrityError as err:
        session.rollback()  # откатываем session.add(new_achievement)
        logger.error(f"Ошибка при сохранении ачивки: {err}")
        return False


def get_user_achievement(user_achievement_id: int) -> AchievementStatus:
    """Достаем ачивку из базы по ее id."""
    user_achievement = (
        session.query(AchievementStatus)
        .filter(AchievementStatus.id == user_achievement_id)
        .first()
    )
    return user_achievement


def create_team(name: str, size: int):
    """Создает новую команду."""
    new_team = Team(name=name, team_size=size)
    session.add(new_team)
    try:
        session.commit()
        logger.info("Новая команда создана.")
        return new_team
    except IntegrityError as err:
        session.rollback()
        logger.error(f"Ошибка при создании команды: {err}")


def set_team_param(
    team: Team, name: str = None, size: int = None, users: list[User] = None
):
    """Сеттер для объекта Команды."""
    if name:
        team.name = name
    if size:
        team.team_size = size
    if users:
        team.users = users
    try:
        session.commit()
        logger.info(f"Команда {team.name} обновлена.")
    except IntegrityError as err:
        session.rollback()
        logger.error(f"Ошибка при редактировании команды: {err}")


def get_all_teams():
    """Возвращает список всех команд."""
    return session.query(Team).all()


def get_team(team_id: int = None, name: str = None):
    """Возвращает объект команды по имени."""
    if team_id:
        return session.query(Team).filter(Team.id == team_id).first()
    elif name:
        return session.query(Team).filter(Team.name == name).first()


def create_category(data: dict):
    """Метод для создания новой категории в базе."""
    new_category = Category(
        name=data.get("name")
    )
    session.add(new_category)
    try:
        session.commit()
        logger.info("Категория добавлена")
        return True
    except IntegrityError as err:
        session.rollback()  # откатываем session.add(new_category)
        logger.error(f"Ошибка при сохранении категории: {err}")
        return False


def get_category(category_id: int = None, name: str = None) -> Category:
    """Достаем категорию из базы по ее id."""
    category = (
        session.query(
            Category).filter(
            Category.id == category_id if category_id
            else Category.name == name
        ).first())
    return category if category else "Unknown Category"


def get_all_categories():
    """Возвращает все категории из базы."""
    return session.query(Category).all()


def set_category_param(category_id: int, name: str = None):
    """Сеттер для обновления свойств объекта Category."""
    category = get_category(category_id)
    if name:
        category.name = name
    try:
        session.commit()
        logger.info("Категория обновлена")
        return True
    except IntegrityError as err:
        logger.error(f"Ошибка при обновлении категории: {err}")
        session.rollback()
        return False


def get_tasks_by_status(status: str) -> list[tuple]:
    """Задания по статусу."""
    return (
        session.query(
            AchievementStatus.id, User.name, Achievement.name, Category.name
        )
        .join(User, AchievementStatus.user_id == User.id)
        .join(Achievement, Achievement.id == AchievementStatus.achievement_id)
        .join(Category, Category.id == Achievement.category_id)
        .filter(AchievementStatus.status == status)
        .all()
    )


def get_tasks_by_achievement_and_status(
    achievement_id: int, status: str
) -> list[tuple]:
    """Задания на проверку для определенной ачивки."""
    return (
        session.query(
            AchievementStatus.id, User.name, Achievement.name, Category.name
        )
        .join(User, AchievementStatus.user_id == User.id)
        .join(Achievement, Achievement.id == AchievementStatus.achievement_id)
        .join(Category, Category.id == Achievement.category_id)
        .filter(
            AchievementStatus.status == status,
            AchievementStatus.achievement_id == achievement_id,
        )
        .all()
    )


def get_tasks_by_achievement_category_and_status(
    category_id: int, status: str
) -> list[tuple]:
    """Задания на проверку в определенной категории."""
    return (
        session.query(
            AchievementStatus.id, User.name, Achievement.name, Category.name
        )
        .join(User, AchievementStatus.user_id == User.id)
        .join(Achievement, Achievement.id == AchievementStatus.achievement_id)
        .join(Category, Category.id == Achievement.category_id)
        .filter(
            AchievementStatus.status == status,
            Achievement.category_id == category_id,
        )
        .all()
    )


def get_categories_with_tasks(status: str) -> Category:
    """Категории, в которых есть задания на проверку."""
    return (
        session.query(Category.id, Category.name)
        .join(Achievement, Category.id == Achievement.category_id)
        .join(
            AchievementStatus,
            Achievement.id == AchievementStatus.achievement_id,
        )
        .filter(AchievementStatus.status == status)
        .distinct()
        .all()
    )


def get_achievements_with_tasks(status: str) -> Achievement:
    """Ачивки, которые сдали на проверку."""
    return (
        session.query(Achievement.id, Achievement.name)
        .join(
            AchievementStatus,
            Achievement.id == AchievementStatus.achievement_id,
        )
        .filter(AchievementStatus.status == status)
        .distinct()
        .all()
    )

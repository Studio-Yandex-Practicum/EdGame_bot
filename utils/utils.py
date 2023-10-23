import logging

from aiogram.types import Message

from db.models import Achievement, Team, User
from utils.db_commands import get_achievement, send_task, user_achievements

from .pagination import pagination_static

logger = logging.getLogger(__name__)


def generate_achievements_list(
    tasks: list[Achievement],
    lexicon: dict,
    current_page: int = 1,
    page_size: int = 5,
    pages: dict = None,
    methodist=False,
) -> dict:
    """Обрабатывает список доступных ачивок и выдает словарь с текстом.

    Для сообщения, словарем id ачивок, информацию для пагинатора,
    если ачивок много, и номер последнего элемента для клавиатуры.
    """
    task_list = []
    task_ids = {}
    count = 0
    if not pages:
        for i in range(len(tasks)):
            count += 1
            task_info = f"{count}: {tasks[i].name}"
            task_list.append(task_info)
            task_ids[count] = tasks[i].id
            # Список описаний, разбитый по страницам
            pages = pagination_static(page_size, task_list)
    if current_page < 1:
        current_page = len(pages)
    elif current_page > len(pages):
        current_page = 1
    new_page = pages[current_page]
    text = "\n\n".join(new_page["objects"])
    msg = (
        f'{lexicon["available_achievements"]}:\n\n'
        f"{text}\n\n"
        f'{lexicon["choose_achievement"]}:'
    )
    if methodist:
        msg = f'{lexicon["available_achievements"]}:\n\n{text}\n\n'
    page_info = {
        "current_page": current_page,
        "first_item": new_page["first_item"],
        "final_item": new_page["final_item"],
        "pages": pages,
        "tasks": tasks,
        "task_ids": task_ids,
        "msg": msg,
    }
    return page_info


async def _check_artifact_type(
    message: Message, artifact_type: str, lexicon: dict
):
    """Проверяет типа артифакта на соответствие заданию."""
    artifact_types = {
        "image": message.photo,
        "video": message.video,
        "document": message.document,
        "audio": message.audio,
        "voice": message.voice,
        "text": message.text,
    }
    artifact = artifact_types[artifact_type]
    if not artifact:
        await message.answer(
            f'{lexicon["ask_artifact_again"]}: {lexicon[artifact_type]}'
        )
        return False
    return artifact


async def process_artifact(
    message: Message, achievement_id: int, lexicon: dict
):
    """Достает id из возможных типов сообщения и сохраняет в базе.

    Информацию об ачивке с новым статусом.
    """
    achievement = get_achievement(achievement_id)
    art_type = achievement.artifact_type
    artifact = await _check_artifact_type(message, art_type, lexicon)
    if not artifact:
        return
    files_id = []
    if art_type == "image":
        files_id.append(artifact[-1].file_id)
    elif art_type != "text" and art_type != "image":
        files_id.append(artifact.file_id)
    user_id = message.from_user.id
    text = message.text if message.text else message.caption
    try:
        send_task(user_id, achievement_id, files_id, text)
        return True
    except Exception as err:
        logger.error(f"Ошибка при сохранении статуса ачивки в базе: {err}")
        return False


async def process_artifact_group(
    messages: list[Message], achievement_id: int, lexicon: dict
):
    """Достает id из возможных типов сообщения и сохраняет в базе.

    Информацию об ачивке с новым статусом.
    """
    achievement = get_achievement(achievement_id)
    art_type = achievement.artifact_type
    files_id = []
    for message in messages:
        artifact = await _check_artifact_type(message, art_type, lexicon)
        if not artifact:
            return
        if art_type == "image":
            files_id.append(artifact[-1].file_id)
        else:
            files_id.append(artifact.file_id)
    user_id = messages[0].from_user.id
    text = messages[0].text if messages[0].text else messages[0].caption
    try:
        send_task(user_id, achievement_id, files_id, text)
        return True
    except Exception as err:
        logger.error(f"Ошибка при сохранении статуса ачивки в базе: {err}")
        return False


def get_achievement_info(
    task_id: type(int or str), lexicon: dict
) -> dict[str, str]:
    """Возвращает словарь с текстом об ачивке для сообщения.

    Пользователю, id изображения и id ачивки.
    """
    task = (
        get_achievement(task_id)
        if isinstance(task_id, int)
        else get_achievement(name=task_id)
    )
    name = task.name
    image = task.image
    description = task.description
    instruction = task.instruction
    artifact_type = task.artifact_type
    task_type = task.achievement_type
    score = task.score
    price = task.price
    info = (
        f'{lexicon["task_name"]}: {name}\n'
        f'{lexicon["score_rate"]}: {score}\n'
        f'{lexicon["task_description"]}: {description}\n'
        f'{lexicon["task_instruction"]}: {instruction}\n'
        f'{lexicon["artifact_type"]}: {lexicon[artifact_type]}\n'
        f'{lexicon["task_type"]}: {lexicon[task_type]}\n'
        f'{lexicon["task_price"]}: {price}'
    )
    return {"info": info, "image": image, "id": task.id}


def generate_text_with_tasks_in_review(user_id: int, lexicon: dict[str, str]):
    """Принимает id пользователя и возвращает текст.

    С инфой об ачивках на проверке для сообщения.
    """
    achievements = user_achievements(user_id)
    in_review = []
    count = 0
    for achievement in achievements:
        # Добавляем описания ачивок в список
        task = achievement[0]
        status = achievement[1]
        if status == "pending":
            count += 1
            task_info = (
                f'{count}: {lexicon["pending_counselor"]}\n'
                f'{lexicon["task_name"]}: {task.name}\n'
                f'{lexicon["task_description"]}: {task.description}'
            )
            in_review.append(task_info)
        if status == "pending_methodist":
            count += 1
            task_info = (
                f'{count}: {lexicon["pending_methodist"]}\n'
                f'{lexicon["task_name"]}: {task.name}\n'
                f'{lexicon["task_description"]}: {task.description}'
            )
            in_review.append(task_info)
    text = "\n\n".join(in_review)
    msg = (
        (
            f'{lexicon["achievements_completed"]}\n\n'
            f"{text}\n\n"
            f'{lexicon["cheer_up"]}'
        )
        if in_review
        else lexicon["no_achievement_completed"]
    )
    return msg


def generate_text_with_reviewed_tasks(user_id: int, lexicon: dict[str, str]):
    """Принимает id пользователя и возвращает текст.

    С инфой о проверенных ачивках для сообщения.
    """
    achievements = user_achievements(user_id)
    reviewed = []
    count = 0
    for achievement in achievements:
        # Добавляем описания ачивок в список
        task = achievement[0]
        status = achievement[1]
        rejection_reason = achievement[2]
        if status == "rejected":
            count += 1
            task_info = (
                f'{count}: {lexicon["status_rejected"]}\n'
                f'{lexicon["rejection_reason"]}: {rejection_reason}'
                f'{lexicon["task_name"]}: {task.name}\n'
                f'{lexicon["task_description"]}: {task.description}'
            )
            reviewed.append(task_info)
        if status == "approved":
            count += 1
            task_info = (
                f'{count}: {lexicon["status_approved"]}\n'
                f'{lexicon["task_name"]}: {task.name}\n'
                f'{lexicon["task_description"]}: {task.description}'
                f'{lexicon["score_added"]}: {task.score}'
            )
            reviewed.append(task_info)
    text = "\n\n".join(reviewed)
    msg = (
        (
            f'{lexicon["achievements_completed"]}\n\n'
            f"{text}\n\n"
            f'{lexicon["cheer_up"]}'
        )
        if reviewed
        else lexicon["no_achievement_reviewed"]
    )
    return msg


def generate_profile_info(user: User, lexicon: dict):
    """Генерирует текст с инфой для личного кабинета."""
    text = (
        f'{lexicon["student_profile"]}\n\n'
        f'{lexicon["lk_info"]}:\n'
        f'{lexicon["name"]} - {user.name}\n'
        f'{lexicon["score"]} - {user.score}\n'
        f"Роль - {user.role}\n"
        f"Номер отряда - {user.group}\n"
    )
    if user.team:
        text += f"Команда - {user.team.name}"
    return text


def generate_users_list(
    users: list[User],
    lexicon: dict,
    current_page: int = 1,
    page_size: int = 5,
    pages: dict = None,
) -> dict:
    """Обрабатывает список объектов, и выдает словарь с текстом.

    Для сообщения, словарем id объектов, информацию для пагинатора,
    если объектов много, и номер последнего элемента для клавиатуры.
    """
    user_list = []
    user_ids = {}
    count = 0
    if not pages:
        for i in range(len(users)):
            count += 1
            user_info = f"{count}: {users[i].name}"
            if users[i].team:
                user_info += f"\n{lexicon['team_name']} - {users[i].team.name}"
            user_list.append(user_info)
            user_ids[count] = users[i].id
            # Список описаний, разбитый по страницам
            pages = pagination_static(page_size, user_list)
    if current_page < 1:
        current_page = len(pages)
    elif current_page > len(pages):
        current_page = 1
    new_page = pages[current_page]
    text = "\n\n".join(new_page["objects"])
    msg = f'{lexicon["choose_team_member"]}:\n\n{text}\n\n'
    page_info = {
        "current_page": current_page,
        "first_item": new_page["first_item"],
        "final_item": new_page["final_item"],
        "pages": pages,
        "users": users,
        "user_ids": user_ids,
        "msg": msg,
    }
    return page_info


def generate_team_info(team: Team, lexicon: dict):
    """Генерирует информацию о команде."""
    members = []
    if team.users:
        members.append(f'{lexicon["team_members"]}\n')
        for user in team.users:
            user_info = (
                f'{lexicon["name"]} - {user.name}\n'
                f'{lexicon["group_number"]} - {user.group}'
            )
            members.append(user_info)
    text = (
        f'{lexicon["team_name"]} - {team.name}\n\n'
        f'{lexicon["team_size"]} - {team.team_size}\n\n'
    )
    if members:
        members_info = "\n".join(members)
        text += members_info
    return text


def generate_teams_list(
    teams: list[Team],
    lexicon: dict,
    current_page: int = 1,
    page_size: int = 5,
    pages: dict = None,
    methodist=False,
) -> dict:
    """Обрабатывает список команд, и выдает словарь с текстом.

    Для сообщения, словарем id объектов, информацию для пагинатора,
    если объектов много, и номер последнего элемента для клавиатуры.
    """
    team_list = []
    team_ids = {}
    count = 0
    if not pages:
        for i in range(len(teams)):
            count += 1
            team_list.append(
                f"{count}: {teams[i].name} - (Занято "
                f"{len(teams[i].users)}/{teams[i].team_size})."
            )
            team_ids[count] = teams[i].id
        # Список описаний, разбитый по страницам
        pages = pagination_static(page_size, team_list)
    if current_page < 1:
        current_page = len(pages)
    elif current_page > len(pages):
        current_page = 1
    new_page = pages[current_page]
    text = "\n\n".join(new_page["objects"])
    msg = f'{lexicon["show_teams_for_child"]}\n\n{text}\n\n'
    if methodist:
        msg = f'{lexicon["show_teams_list"]}:\n\n{text}\n\n'
    page_info = {
        "current_page": current_page,
        "first_item": new_page["first_item"],
        "final_item": new_page["final_item"],
        "pages": pages,
        "teams": teams,
        "team_ids": team_ids,
        "msg": msg,
    }
    return page_info

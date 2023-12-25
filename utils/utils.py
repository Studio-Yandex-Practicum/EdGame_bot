import logging
from typing import Callable

from aiogram.types import Message
from sqlalchemy import Row

from db.models import Achievement, Category, Team, User
from utils.db_commands import (
    get_achievement,
    get_category,
    get_info_for_methodist_profile,
    send_task,
    user_achievements,
)

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
    """Пагинированный список ачивок.

    Обрабатывает список доступных ачивок и выдает словарь с текстом для
    сообщения, словарем id ачивок, информацию для пагинатора,
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
    message: Message, achievement_id: int, lexicon: dict, user: User, session
) -> bool:
    """Сохраняет статус ачивки.

    Достает id из возможных типов сообщения и сохраняет в базе информацию об
    ачивке с новым статусом.
    """
    achievement = get_achievement(session, achievement_id)
    art_type = achievement.artifact_type
    artifact = await _check_artifact_type(message, art_type, lexicon)
    if not artifact:
        return
    files_id = []
    if art_type == "image":
        files_id.append(artifact[-1].file_id)
    elif art_type != "text" and art_type != "image":
        files_id.append(artifact.file_id)
    text = message.text if message.text else message.caption
    try:
        send_task(session, user, achievement, files_id, text)
        return True
    except Exception as err:
        logger.error(f"Ошибка при сохранении статуса ачивки в базе: {err}")
        return False


async def process_artifact_group(
    messages: list[Message],
    achievement_id: int,
    lexicon: dict,
    user: User,
    session,
) -> bool:
    """Сохраняет статус ачивки.

    Достает id из возможных типов сообщения и сохраняет в базе информацию
    об ачивке с новым статусом.
    """
    achievement = get_achievement(session, achievement_id)
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
    text = messages[0].text if messages[0].text else messages[0].caption
    try:
        send_task(session, user, achievement, files_id, text)
        return True
    except Exception as err:
        logger.error(f"Ошибка при сохранении статуса ачивки в базе: {err}")
        return False


def get_achievement_info(
    task_id: type(int or str), lexicon: dict, session
) -> dict[str, str]:
    """Информация об ачивке.

    Возвращает словарь с текстом об ачивке для сообщения пользователю,
    id изображения и id ачивки.
    """
    task = (
        get_achievement(session, task_id)
        if isinstance(task_id, int)
        else get_achievement(session, name=task_id)
    )
    name = task.name
    image = task.image
    description = task.description
    instruction = task.instruction
    artifact_type = task.artifact_type
    task_type = task.achievement_type
    score = task.score
    price = task.price
    category = task.category_id
    if not category:
        category = lexicon["task_not_category"]
    info = (
        f'{lexicon["task_name"]}: {name}\n'
        f'{lexicon["score_rate"]}: {score}\n'
        f'{lexicon["task_description"]}: {description}\n'
        f'{lexicon["task_instruction"]}: {instruction}\n'
        f'{lexicon["artifact_type"]}: {lexicon[artifact_type]}\n'
        f'{lexicon["task_type"]}: {lexicon[task_type]}\n'
        f'{lexicon["task_category"]}: {category}\n'
        f'{lexicon["task_price"]}: {price}'
    )
    return {"info": info, "image": image, "task": task, "id": task.id}


def generate_achievement_message_for_kid(
    lexicon: dict, text: str, user: User, achievement: Achievement
) -> str:
    """Сообщение на странице отдельной ачивки в зависимости от роли ребенка."""
    header = "achievement_chosen"
    if achievement.achievement_type == "individual":
        footer = "fulfil_individual_achievement"
    else:
        footer = (
            "fulfil_team_achievement"
            if user.captain_of_team_id
            else "available_for_team_captain_only"
        )
    msg = message_pattern(lexicon, text, header, footer)
    return msg


def generate_text_with_tasks_in_review(
    user_id: int, lexicon: dict[str, str], session
):
    """Ачивки, сданные на проверку.

    Принимает id пользователя и возвращает текст с инфой об ачивках на
    проверке для сообщения.
    """
    achievements = user_achievements(session, user_id)
    in_review = []
    count = 0
    for achievement in achievements:
        # Добавляем описания ачивок в список
        task = achievement[0]
        status = achievement[1]
        if status == "pending":
            count += 1
            task_info = (
                f'{count}: {lexicon["pending_counsellor"]}\n'
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


def generate_text_with_reviewed_tasks(
    user_id: int, lexicon: dict[str, str], session
):
    """Список проверенных ачивок.

    Принимает id пользователя и возвращает текст с инфой о проверенных
    ачивках для сообщения.
    """
    achievements = user_achievements(session, user_id)
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
    """
    Пагинированный список пользователей.

    Обрабатывает список объектов и выдает словарь с текстом для
    сообщения, словарем id объектов, информацию для пагинатора,
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
    """
    Пагинированный список команд.

    Обрабатывает список команд и выдает словарь с текстом для
    сообщения, словарем id объектов, информацию для пагинатора,
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


def get_category_info(
    category_id: type(int or str), lexicon: dict, session
) -> dict[str, str]:
    """Возвращает словарь с названием категории для сообщения пользователю."""
    category = (
        get_category(session, category_id)
        if isinstance(category_id, int)
        else get_category(session, name=category_id)
    )
    name = category.name
    info = f'{lexicon["category_name"]}: {name}'
    return {"info": info, "id": category.id}


def generate_categories_list(
    categories: list[Category],
    lexicon: dict,
    current_page: int = 1,
    page_size: int = 5,
    pages: dict = None,
    methodist=False,
) -> dict:
    """Обрабатывает список доступных категорий.

    Выдает словарь с текстом для сообщения, словарем id категорий, информацию
    для пагинатора, если категорий много, и номер последнего элемента для
    клавиатуры.
    """
    categories_list = []
    categories_ids = {}
    count = 0
    if not pages:
        for i in range(len(categories)):
            count += 1
            categories_info = f"{count}: {categories[i].name}"
            categories_list.append(categories_info)
            categories_ids[count] = categories[i].id
        # Список описаний, разбитый по страницам
        pages = pagination_static(page_size, categories_list)
    if current_page < 1:
        current_page = len(pages)
    elif current_page > len(pages):
        current_page = 1
    new_page = pages[current_page]
    text = "\n\n".join(new_page["objects"])
    msg = f'{lexicon["available_categories"]}:\n\n' f"{text}\n\n"
    if methodist:
        msg = f'{lexicon["available_categories"]}:\n\n{text}\n\n'
    page_info = {
        "current_page": current_page,
        "first_item": new_page["first_item"],
        "final_item": new_page["final_item"],
        "pages": pages,
        "categories": categories,
        "categories_ids": categories_ids,
        "msg": msg,
    }
    return page_info


def generate_objects_list(
    objects: list | list[Row],
    lexicon: dict,
    msg: Callable,
    obj_info: Callable,
    current_page: int = 1,
    page_size: int = 5,
    pages: dict = None,
) -> dict:
    """
    Обрабатывает список доступных объектов моделей данных.

    Выдает словарь с текстом для сообщения, словарем id объектов моделей
    данных, информацию для пагинатора, если объектов моделей данных много,
    и номер последнего элемента для клавиатуры.

    :objects - запрос из базы, который нужно пагинировать. Первый элемент
        должен быть id [Row(1, ),].
    :msg - шаблон сообщения.
    :obj_info - шаблон объекта для пагинации.
    """
    objects_list = []
    objects_ids = {}

    if not pages:
        for count, obj in enumerate(objects, start=1):
            objects_ids[count] = obj[0]

            info = obj_info(lexicon, count, obj)
            objects_list.append(info)

        pages = pagination_static(page_size, objects_list)

    if current_page < 1:
        current_page = len(pages)
    elif current_page > len(pages):
        current_page = 1
    new_page = pages[current_page]

    text = "\n\n".join(new_page["objects"])
    msg = f"{msg(lexicon, text)}"

    page_info = {
        "current_page": current_page,
        "first_item": new_page["first_item"],
        "final_item": new_page["final_item"],
        "pages": pages,
        "objects": objects,
        "objects_ids": objects_ids,
        "msg": msg,
    }
    return page_info


def message_pattern(lexicon: dict, text: str, header: str, footer: str) -> str:
    msg = f"{lexicon[header]}:\n\n" f"{text}\n\n" f"{lexicon[footer]}"
    return msg


def task_info(lexicon: dict, count: int, obj: tuple, *args, **kwargs) -> str:
    *_, kid, achievement, category = obj
    category = category if category is not None else lexicon["uncategorized"]
    info = (
        f"<b>{count}.</b>\n"
        f"<b>{lexicon['category']}:</b> {category}\n"
        f"<b>{lexicon['achievement']}:</b> {achievement}\n"
        f"<b>{lexicon['sender']}:</b> {kid}\n"
    )
    return info


def object_info(lexicon: dict, count: int, obj, *args, **kwargs) -> str:
    *_, name = obj

    info = f"{count}. {name}"
    return info


def methodist_profile_info(lexicon: dict, user: User, session) -> str:
    """Текст в профиле методиста."""
    query = get_info_for_methodist_profile(session)

    info = (
        f"{lexicon['methodist_profile']}\n\n"
        f"<b>{lexicon['name']}</b> - {user.name}\n"
        f"<b>{lexicon['teams']}</b> - {query['teams_count']}\n"
        f"<b>{lexicon['children']}</b> - {query['children_count']}\n"
        f"<b>{lexicon['categories']}</b> - {query['categories_count']}\n"
        f"<b>{lexicon['achievements']}</b> - {query['achievements_count']}\n"
        f"<b>{lexicon['tasks']}</b> - {query['tasks_count']}\n"
    )
    return info


def generate_achievements_list_category(
    tasks: list[Achievement],
    lexicon: dict,
    current_page: int = 1,
    page_size: int = 5,
    pages: dict = None,
) -> dict:
    """Пагинированный список ачивок.

    Обрабатывает список доступных ачивок и выдает словарь с текстом для
    сообщения, словарем id ачивок, информацию для пагинатора,
    если ачивок много, и номер последнего элемента для клавиатуры.
    """
    task_list = []
    task_ids = {}
    count = 0
    if not pages:
        for i in range(len(tasks)):
            count += 1
            task_info = (
                f"{count}: Название - {tasks[i].name}, "
                f"Описание - {tasks[i].description}, "
                f"Цена - {tasks[i].price}, "
                f"начальные баллы - {tasks[i].score}\n"
            )
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
    msg = f'{lexicon["category_achievement"]}:\n\n' f"{text}\n\n"
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


async def data_for_multiselect_kb(queryset):
    """Данные для клавиатуры с множественным выбором."""
    data = {}
    for row in queryset:
        data[row.id] = {"name": row.name, "selected": False}
    return data

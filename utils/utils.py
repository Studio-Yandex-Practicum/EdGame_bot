import logging

from aiogram.types import Message

from utils.db_commands import send_task, get_achievement, user_achievements
from db.models import Achievement, User

logger = logging.getLogger(__name__)


def process_next_achievements(
    tasks: list[Achievement],
    count: int = 0,
    previous_final_item: int = 0,
    page_size: int = 5,
) -> tuple:
    """
    Обрабатывает список доступных ачивок и выдает кортеж с текстом для
    сообщения, словарем id ачивок, информацию для пагинатора,
    если ачивок много, и номер последнего элемента для клавиатуры.
    """
    task_list = []
    task_ids = {}
    # Устанавливаем номер последнего элемента
    new_final_item = previous_final_item + page_size
    # Размер страницы
    final_item = (
        len(tasks) if len(tasks) < (new_final_item + 1) else new_final_item
    )
    for i in range(previous_final_item, final_item):
        count += 1
        task_list.append(f"{count}: {tasks[i].name}.")
        task_ids[count] = tasks[i].id
    text = "\n\n".join(task_list)
    task_info = {"count": count, "final_item": final_item, "tasks": tasks}
    return (text, task_ids, task_info)


def process_previous_achievements(
    tasks: list[Achievement],
    count: int = 0,
    previous_final_item: int = 0,
    page_size: int = 5,
) -> tuple:
    """
    Обрабатывает список доступных ачивок и выдает кортеж с текстом для
    сообщения, словарем id ачивок, информацию для пагинатора,
    если ачивок много, и номер последнего элемента для клавиатуры.
    """
    task_list = []
    task_ids = {}
    # Счетчик id
    count = count - page_size * 2 if count > page_size * 2 else 0
    # Устанавливаем номер последнего элемента
    new_final_item = previous_final_item - page_size
    # Устанавливаем номер первого элемента
    first_item = (
        previous_final_item - page_size * 2
        if previous_final_item > page_size * 2
        else 0
    )
    # Размер страницы
    final_item = (
        len(tasks) if len(tasks) < (new_final_item + 1) else new_final_item
    )
    for i in range(first_item, final_item):
        count += 1
        task_list.append(f"{count}: {tasks[i].name}.")
        task_ids[count] = tasks[i].id
    text = "\n\n".join(task_list)
    task_info = {
        "count": count,
        "first_item": first_item,
        "final_item": final_item,
        "tasks": tasks,
    }
    return (text, task_ids, task_info)


async def process_artifact(
    message: Message, achievement_id: int, lexicon: dict
):
    """
    Достает id из возможных типов сообщения и сохраняет в базе
    информацию об ачивке с новым статусом.
    """
    artifact_types = {
        "photo": message.photo,
        "video": message.video,
        "document": message.document,
        "audio": message.audio,
        "voice": message.voice,
    }
    achievement = get_achievement(achievement_id)
    art_type = achievement.artifact_type
    artifact = artifact_types[art_type]
    if not artifact:
        await message.answer(
            f'{lexicon["ask_artifact_again"]}: {lexicon[art_type]}'
        )
    user_id = message.from_user.id
    files_id = []
    if art_type == "photo":
        files_id.append(artifact[0].file_id)
    else:
        files_id.append(artifact.file_id)
    text = message.text if message.text else message.caption
    try:
        send_task(user_id, achievement_id, files_id, text)
        return True
    except Exception as err:
        logger.error(f"Ошибка при сохранении статуса ачивки в базе: {err}")
        return False


def get_achievement_info(
    task_id: type(int or str), lexicon: dict
) -> dict[str, str]:
    """
    Возвращает словарь с текстом об ачивке для сообщения
    пользователю, id изображения и id ачивки.
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


def generate_text_with_available_tasks(user_id: int, lexicon: dict[str, str]):
    """
    Принимает id пользователя и возвращает текст
    с инфой о доступных ачивках для сообщения.
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
                f'{count}: {lexicon["pending_councelor"]}\n'
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
    return "\n\n".join(in_review) if in_review else False


def generate_text_with_reviewed_tasks(user_id: int, lexicon: dict[str, str]):
    """
    Принимает id пользователя и возвращает текст
    с инфой о проверенных ачивках для сообщения.
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
    return "\n\n".join(reviewed) if reviewed else False


def generate_profile_info(user: User, lexicon: dict):
    """Генерирует текст с инфой для личного кабинета."""
    text = (
        f'{lexicon["student_profile"]}\n\n'
        f'{lexicon["lk_info"]}:\n'
        f'{lexicon["name"]} - {user.name}\n'
        f'{lexicon["score"]} - {user.score}\n'
        f"Роль - {user.role}"
    )
    return text

from aiogram.fsm.state import State, StatesGroup


class Data(StatesGroup):
    """
    Машина состояний для реализации сценариев диалогов с пользователем.
    """
    name = State()
    language = State()
    change_name = State()
    change_bio = State()
    change_language = State()
    task_id = State()
    tasks = State()
    tasks_info = State()
    artifact = State()


class Profile(StatesGroup):
    """
    Машина состояний для анкетирования при старте бота.
    """
    choose_language = State()
    get_name = State()
    get_group = State()


class TaskList(StatesGroup):
    """
    Машина состояний для отображения списка ачивок у методиста.
    """
    user_language = State()
    tasks = State()
    tasks_for_review = State()
    task_ids = State()
    task_info = State()


class AddTask(StatesGroup):
    """
    Машина состояний для добавления ачивки в базу методистом.
    """
    user_language = State()
    task_id = State()
    image = State()
    name = State()
    description = State()
    instruction = State()
    price = State()
    score = State()
    artifact_type = State()
    achievement_type = State()
    confirm_task = State()


class EditTask(StatesGroup):
    """
    Машина состояний для редактирования ачивки методистом.
    """
    user_language = State()
    task_id = State()
    image = State()
    name = State()
    description = State()
    instruction = State()
    price = State()
    score = State()
    artifact_type = State()
    achievement_type = State()
    confirm_task = State()


class ReviewTask(StatesGroup):
    """
    Машина состояний для проверки ачивки методистом.
    """
    pending = State()
    task_id = State()
    user_language = State()
    reject_message = State()

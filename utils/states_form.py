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

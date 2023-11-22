from aiogram.fsm.state import State, StatesGroup


class Data(StatesGroup):
    """Машина состояний для реализации сценариев диалогов с пользователем."""

    name = State()
    language = State()
    change_name = State()
    change_bio = State()
    change_language = State()
    task_id = State()
    tasks = State()
    task_ids = State()
    pagination_info = State()
    fulfil_achievement = State()
    artifact = State()
    child = State()
    query_id = State()
    category = State()


class Profile(StatesGroup):
    """Машина состояний для анкетирования при старте бота."""

    choose_language = State()
    get_name = State()
    get_group = State()


class TaskList(StatesGroup):
    """Машина состояний для отображения списка ачивок у методиста."""

    language = State()
    tasks = State()
    cd = State()
    tasks_for_review = State()
    task_ids = State()
    task_info = State()
    current_page = State()
    query_id = State()


class AddTask(StatesGroup):
    """Машина состояний для добавления ачивки в базу методистом."""

    language = State()
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
    category = State()


class EditTask(StatesGroup):
    """Машина состояний для редактирования ачивки методистом."""

    language = State()
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
    query_id = State()
    achievements_category = State()


class ReviewTask(StatesGroup):
    """Машина состояний для проверки ачивки методистом."""

    pending = State()
    task_id = State()
    language = State()
    reject_message = State()


class CreateTeam(StatesGroup):
    """Машина состояний для создания команды."""

    name = State()
    size = State()
    team = State()
    add_members = State()
    choose_member = State()
    language = State()
    ready = State()
    child = State()
    children = State()
    children_ids = State()
    pagination_info = State()


class EditTeam(StatesGroup):
    """Машина состояний для создания команды."""

    name = State()
    size = State()
    team = State()
    query_id = State()
    teams = State()
    team_ids = State()
    add_members = State()
    choose_member = State()
    language = State()
    ready = State()
    child = State()
    children = State()
    children_ids = State()
    pagination_info = State()
    current_page = State()
    current_page_children = State()


class JoinTeam(StatesGroup):
    """Машина состояний для присоединения к команде."""

    team_chosen = State()
    join_team = State()
    language = State()
    team = State()
    team_id = State()
    query_id = State()
    teams = State()
    team_ids = State()
    child = State()
    pagination_info = State()
    become_captain = State()


class AddCategory(StatesGroup):
    """Машина состояний для добавления категории в базу методистом."""

    language = State()
    category_id = State()
    name = State()
    confirm_task = State()


class EditCategory(StatesGroup):
    """Машина состояний для редактирования категории методистом."""

    language = State()
    category_id = State()
    name = State()
    confirm_task = State()
    query_id = State()


class CategoryList(StatesGroup):
    """Машина состояний для отображения списка категорий у методиста."""

    language = State()
    categories = State()
    category_ids = State()
    category_info = State()
    current_page = State()
    query_id = State()


class EnteringPassword(StatesGroup):
    """Машина состояний для ввода пароля."""

    psw2hash = State()


class CounsellorPassword(StatesGroup):
    """Машина состояний для ввода пароля для вожатого."""

    psw2hash = State()


class MethodistPassword(StatesGroup):
    """Машина состояний для ввода пароля для методиста."""

    psw2hash = State()


class MasterPassword(StatesGroup):
    """Машина состояний для ввода мастер-пароля."""

    psw2hash = State()

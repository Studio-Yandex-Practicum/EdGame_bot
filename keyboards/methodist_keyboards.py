from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import BUTTONS, LEXICON


# Кнопки при уведомлении о поступивших артефактах
def art_list_keyboard(language: str) -> ReplyKeyboardMarkup:
    """Кнопки при входящем уведомлении методисту."""
    buttons = BUTTONS[language]
    tasks_for_review = KeyboardButton(text=buttons["tasks_for_review"])
    lk = KeyboardButton(text=buttons["lk"])

    keyboard = [[tasks_for_review], [lk]]
    markup = ReplyKeyboardMarkup(
        keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True
    )
    return markup


# Кнопки в личном кабинете
def methodist_profile_keyboard(language: str) -> ReplyKeyboardMarkup:
    """Генерирует клавиатуру в ЛК методиста."""
    buttons = BUTTONS[language]
    add_task = KeyboardButton(text=buttons["add_task"])
    achievement_list = KeyboardButton(text=buttons["achievement_list"])
    tasks_for_review = KeyboardButton(text=buttons["tasks_for_review"])
    edit_profile = KeyboardButton(text=buttons["edit_profile"])
    create_team = KeyboardButton(text=buttons["create_team"])
    team_list = KeyboardButton(text=buttons["team_list"])
    help_button = KeyboardButton(text=buttons["help"])
    add_category = KeyboardButton(text=buttons["add_category"])
    category_list = KeyboardButton(text=buttons["category_list"])

    keyboard = [
        [add_task, add_category, create_team],
        [tasks_for_review],
        [achievement_list],
        [category_list],
        [team_list],
        [edit_profile],
        [help_button],
    ]
    markup = ReplyKeyboardMarkup(
        keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True
    )
    return markup


def add_task_keyboard(language: str) -> InlineKeyboardMarkup:
    """Генерирует инлайн клавиатуру в разделе добавления задания."""
    buttons = BUTTONS[language]
    ready = InlineKeyboardButton(text=buttons["ready"], callback_data="ready")
    lk = InlineKeyboardButton(text=buttons["lk"], callback_data="profile")
    markup = InlineKeyboardMarkup(inline_keyboard=[[ready], [lk]])
    return markup


def task_type_keyboard(language: str) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру при выборе типа ачивки."""
    buttons = LEXICON[language]
    individual = InlineKeyboardButton(
        text=buttons["individual"], callback_data="individual"
    )
    teamwork = InlineKeyboardButton(
        text=buttons["teamwork"], callback_data="teamwork"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[[individual, teamwork]])
    return markup


def artifact_type_keyboard(language: str) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру при выборе типа артефакта."""
    buttons = LEXICON[language]
    text = InlineKeyboardButton(text=buttons["text"], callback_data="text")
    image = InlineKeyboardButton(text=buttons["image"], callback_data="image")
    video = InlineKeyboardButton(text=buttons["video"], callback_data="video")
    markup = InlineKeyboardMarkup(inline_keyboard=[[text, image, video]])
    return markup


def confirm_task_keyboard(language: str) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру при подтверждении добавления задания."""
    buttons = BUTTONS[language]
    confirm_adding_task = InlineKeyboardButton(
        text=buttons["confirm_adding_task"], callback_data="confirm"
    )
    edit_task = InlineKeyboardButton(
        text=buttons["edit_task"], callback_data="edit_task"
    )
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[confirm_adding_task, edit_task]]
    )
    return markup


def edit_task_keyboard(language: str, cd: str = None) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру в разделе редактирования ачивки."""
    buttons = BUTTONS[language]
    name = InlineKeyboardButton(
        text=buttons["edit_name"], callback_data="edit_name"
    )
    image = InlineKeyboardButton(
        text=buttons["edit_image"], callback_data="edit_image"
    )
    description = InlineKeyboardButton(
        text=buttons["edit_description"], callback_data="edit_description"
    )
    instruction = InlineKeyboardButton(
        text=buttons["edit_instruction"], callback_data="edit_instruction"
    )
    task_type = InlineKeyboardButton(
        text=buttons["edit_task_type"], callback_data="edit_task_type"
    )
    artifact_type = InlineKeyboardButton(
        text=buttons["edit_artifact_type"], callback_data="edit_artifact_type"
    )
    score = InlineKeyboardButton(
        text=buttons["edit_score"], callback_data="edit_score"
    )
    price = InlineKeyboardButton(
        text=buttons["edit_price"], callback_data="edit_price"
    )
    achievements_category = InlineKeyboardButton(
        text=buttons["edit_achievements_category"],
        callback_data="edit_achievements_category"
    )
    complete = InlineKeyboardButton(
        text=buttons["complete_editing_task"],
        callback_data=f"back_to_task:{cd}",
    )
    keyboard = [
        [name, image],
        [description, instruction],
        [task_type, artifact_type],
        [score, price],
        [achievements_category],
        [complete],
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


def task_keyboard_methodist(language: str) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру с кнопками в отдельной ачивке."""
    buttons = BUTTONS[language]
    lk = InlineKeyboardButton(text=buttons["lk"], callback_data="profile")
    achievement_list = InlineKeyboardButton(
        text=buttons["back"], callback_data="back_to_achievement_list"
    )
    edit_task = InlineKeyboardButton(
        text=buttons["edit_task"], callback_data="edit_task"
    )
    keyboard = [[edit_task], [achievement_list], [lk]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


def review_keyboard_methodist(language: str, cd: str) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру с кнопками проверки ачивки."""
    buttons = BUTTONS[language]
    lk = InlineKeyboardButton(text=buttons["lk"], callback_data="profile")
    back = InlineKeyboardButton(text=buttons["back"], callback_data=cd)
    approve = InlineKeyboardButton(
        text=buttons["approve"], callback_data="approve"
    )
    reject = InlineKeyboardButton(
        text=buttons["reject"], callback_data="reject"
    )
    keyboard = [[approve], [reject], [back], [lk]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


def create_team_keyboard(language: str) -> InlineKeyboardMarkup:
    """Клавиатура для начала или отмены создания команды."""
    buttons = BUTTONS[language]
    ready = InlineKeyboardButton(
        text=buttons["ready"], callback_data="ready_create_team"
    )
    cancel = InlineKeyboardButton(
        text=buttons["cancel"], callback_data="cancel_create_team"
    )
    keyboard = [[ready, cancel]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


def choose_team_size_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопками для выбора размера команды."""
    buttons = []
    for i in range(2, 11):
        button = InlineKeyboardButton(text=i, callback_data=f"size:{i}")
        buttons.append(button)
    builder = InlineKeyboardBuilder()
    builder.row(*buttons, width=5)
    return builder.as_markup()


def add_members_or_pass_keyboard(language: str) -> InlineKeyboardMarkup:
    """Клавиатура Добавить участников или Пропустить."""
    buttons = BUTTONS[language]
    add_members = InlineKeyboardButton(
        text=buttons["add_team_members"], callback_data="add_team_members"
    )
    pass_adding = InlineKeyboardButton(
        text=buttons["pass"], callback_data="pass_adding_members"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[[add_members, pass_adding]])
    return markup


def choose_member_keyboard(
    language: str, cd: str = None
) -> InlineKeyboardMarkup:
    """Клавиатура при просмотре информации о ребенке."""
    buttons = BUTTONS[language]
    choose = InlineKeyboardButton(
        text=buttons["add"], callback_data="choose_member"
    )
    back = InlineKeyboardButton(
        text=buttons["back"],
        callback_data="back_to_children_list" if not cd else cd,
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[[back, choose]])
    return markup


def delete_user_from_team_keyboard(
    language: str, cd: str = None
) -> InlineKeyboardMarkup:
    """Клавиатура при просмотре информации о ребенке, добавленном в команду."""
    buttons = BUTTONS[language]
    delete = InlineKeyboardButton(
        text=buttons["delete_from_team"], callback_data="delete_member"
    )
    back = InlineKeyboardButton(
        text=buttons["back"],
        callback_data="back_to_children_list" if not cd else cd,
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[[back, delete]])
    return markup


def team_limit_reached_keyboard(
    language: str, cd: str = None
) -> InlineKeyboardMarkup:
    """Клавиатура при просмотре информации о ребенке."""
    buttons = BUTTONS[language]
    back = InlineKeyboardButton(
        text=buttons["back"],
        callback_data="back_to_children_list" if not cd else cd,
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[[back]])
    return markup


def team_keyboard_methodist(language: str) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру с кнопками в отдельной ачивке."""
    buttons = BUTTONS[language]
    back = InlineKeyboardButton(
        text=buttons["back"], callback_data="back_to_team_list"
    )
    edit_team = InlineKeyboardButton(
        text=buttons["edit_team"], callback_data="edit_team"
    )
    add_members = InlineKeyboardButton(
        text=buttons["edit_team_members"], callback_data="edit_team_members"
    )
    keyboard = [[edit_team, add_members], [back]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


def edit_team_keyboard(language: str, cd: str = None) -> InlineKeyboardMarkup:
    """Клавиатура при старте редактирования свойств команды."""
    buttons = BUTTONS[language]
    edit_team_size = InlineKeyboardButton(
        text=buttons["team_size"], callback_data="edit_team_size"
    )
    edit_team_name = InlineKeyboardButton(
        text=buttons["team_name"], callback_data="edit_team_name"
    )
    complete = InlineKeyboardButton(
        text=buttons["complete_editing_task"],
        callback_data=f"back_to_team:{cd}",
    )
    keyboard = [[edit_team_name, edit_team_size], [complete]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


def add_category_keyboard(language: str) -> InlineKeyboardMarkup:
    """Генерирует инлайн клавиатуру в разделе добавления категории."""
    buttons = BUTTONS[language]
    ready = InlineKeyboardButton(
        text=buttons["ready"],
        callback_data="ready_category"
    )
    lk = InlineKeyboardButton(
        text=buttons["lk"],
        callback_data="profile"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[[ready], [lk]])
    return markup


def confirm_category_keyboard(language: str) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру при подтверждении добавления категории."""
    buttons = BUTTONS[language]
    confirm_adding_category = InlineKeyboardButton(
        text=buttons["confirm_adding_category"],
        callback_data="confirm"
    )
    edit_category = InlineKeyboardButton(
        text=buttons["edit_category"],
        callback_data="edit_category"
    )
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[confirm_adding_category, edit_category]]
    )
    return markup


def edit_category_keyboard(
    language: str, cd: str = None
) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру в разделе редактирования категории."""
    buttons = BUTTONS[language]
    name = InlineKeyboardButton(
        text=buttons["edit_category_name"],
        callback_data="edit_category_name"
    )
    complete = InlineKeyboardButton(
        text=buttons["complete_editing_category"],
        callback_data=f"back_to_category:{cd}"
    )
    keyboard = [
        [name],
        [complete]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


def choice_tasks_for_review_keyboard(language: str) -> InlineKeyboardMarkup:
    """Выбор заданий на проверку."""
    buttons = BUTTONS[language]
    all_tasks = InlineKeyboardButton(
        text=buttons["all_tasks"], callback_data="all_tasks"
    )
    achievement_category = InlineKeyboardButton(
        text=buttons["achievement_category"],
        callback_data="choice_category",
    )
    all_achievements = InlineKeyboardButton(
        text=buttons["all_achievements"],
        callback_data="choice_achievement",
    )
    keyboard = [
        [all_tasks],
        [achievement_category],
        [all_achievements],
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


def category_keyboard_methodist(language: str) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру с кнопками в отдельной категории."""
    buttons = BUTTONS[language]
    lk = InlineKeyboardButton(
        text=buttons["lk"],
        callback_data="profile"
    )
    category_list = InlineKeyboardButton(
        text=buttons["back_to_category_list"],
        callback_data="back_to_category_list"
    )
    edit_category = InlineKeyboardButton(
        text=buttons["edit_category"],
        callback_data="edit_category"
    )
    keyboard = [
        [edit_category],
        [category_list],
        [lk]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


def add_achievements_category(language: str) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру в разделе добавления категории для ачивки."""
    buttons = BUTTONS[language]
    add_achievements_category = InlineKeyboardButton(
        text=buttons["add_achievements_category"],
        callback_data="add_achievements_category"
    )
    skip = InlineKeyboardButton(
        text=buttons["skip"],
        callback_data="skip"
    )
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[add_achievements_category], [skip]]
    )
    return markup


def confirm_achievements_category(language: str) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру в разделе добавления категории для ачивки."""
    buttons = BUTTONS[language]
    confirm_achievements_category = InlineKeyboardButton(
        text=buttons["confirm_achievements_category"],
        callback_data="confirm_achievements_category"
    )
    back_to_list_category = InlineKeyboardButton(
        text=buttons["back_to_list_category"],
        callback_data="back_to_list_category"
    )
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [confirm_achievements_category],
            [back_to_list_category]
        ]
    )
    return markup


def continue_job_keyboard(language: str, cd: str) -> InlineKeyboardMarkup:
    buttons = BUTTONS[language]
    lk = InlineKeyboardButton(text=buttons["lk"], callback_data="profile")
    continue_btn = InlineKeyboardButton(
        text=buttons["continue"],
        callback_data=cd,
    )
    tasks_for_review = InlineKeyboardButton(
        text=buttons["tasks_for_review"],
        callback_data="back_tasks_for_review",
    )
    keyboard = [[continue_btn], [tasks_for_review], [lk]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup

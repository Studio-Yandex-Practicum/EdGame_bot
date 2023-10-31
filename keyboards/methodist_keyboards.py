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

    keyboard = [
        [add_task, create_team],
        [tasks_for_review],
        [achievement_list],
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
    """Генерирует клавиатуру в разделе редактирования заявки."""
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
    complete = InlineKeyboardButton(
        text=buttons["complete_editing_task"],
        callback_data=f"back_to_task:{cd}",
    )
    keyboard = [
        [name, image],
        [description, instruction],
        [task_type, artifact_type],
        [score, price],
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


def review_keyboard_methodist(language: str):
    """Генерирует клавиатуру с кнопками проверки ачивки."""
    buttons = BUTTONS[language]
    lk = InlineKeyboardButton(text=buttons["lk"], callback_data="profile")
    tasks_for_review = InlineKeyboardButton(
        text=buttons["tasks_for_review"], callback_data="tasks_for_review"
    )
    approve = InlineKeyboardButton(
        text=buttons["approve"], callback_data="approve"
    )
    reject = InlineKeyboardButton(
        text=buttons["reject"], callback_data="reject"
    )
    keyboard = [[approve], [reject], [tasks_for_review], [lk]]
    return keyboard


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

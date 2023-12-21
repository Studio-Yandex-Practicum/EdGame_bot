from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from lexicon.lexicon import BUTTONS


# Функция, генерирующая клавиатуру для выбора языка
def create_welcome_keyboard() -> InlineKeyboardMarkup:
    # Создаем объекты инлайн-кнопок
    rus_lang: InlineKeyboardButton = InlineKeyboardButton(
        text="Русский язык", callback_data="RU"
    )
    tatar_lang: InlineKeyboardButton = InlineKeyboardButton(
        text="Татар теле", callback_data="TT"
    )
    eng_lang: InlineKeyboardButton = InlineKeyboardButton(
        text="English language", callback_data="EN"
    )
    # Создаем объект инлайн-клавиатуры
    welcome_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[rus_lang], [tatar_lang], [eng_lang]]
    )
    return welcome_keyboard


# Создание клавиатуры для роли ребенка
def menu_keyboard(language: str) -> ReplyKeyboardMarkup:
    """Генерирует клавиатуру с кнопками в главном меню."""
    buttons = BUTTONS[language]
    write_to_methodist = KeyboardButton(text=buttons["write_to_methodist"])
    lk = KeyboardButton(text=buttons["lk"])
    help_button = KeyboardButton(text=buttons["help"])

    keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
        keyboard=[[lk], [help_button], [write_to_methodist]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboard


# Личный кабинет
def profile_keyboard(language: str) -> ReplyKeyboardMarkup:
    """Генерирует клавиатуру с кнопками в личном кабинете."""
    buttons = BUTTONS[language]
    edit_profile = KeyboardButton(text=buttons["edit_profile"])
    available_achievements = KeyboardButton(
        text=buttons["available_achievements"]
    )
    current_achievements = KeyboardButton(text=buttons["current_achievements"])
    reviewed_achievements = KeyboardButton(
        text=buttons["reviewed_achievements"]
    )
    write_to_counsellor = KeyboardButton(text=buttons["write_to_counsellor"])
    help_button = KeyboardButton(text=buttons["help"])
    join_team = KeyboardButton(text=buttons["join_team"])
    category = KeyboardButton(text=buttons["category"])
    keyboard = [
        [available_achievements, current_achievements],
        [reviewed_achievements, join_team],
        [edit_profile],
        [category],
        [help_button, write_to_counsellor],
    ]
    markup = ReplyKeyboardMarkup(
        keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True
    )
    return markup


# Кнопки inline


# Редактирование профиля
def edit_profile_keyboard(language: str) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру с кнопками в редактировании профиля."""
    buttons = BUTTONS[language]
    change_firstname = InlineKeyboardButton(
        text=buttons["change_firstname"], callback_data="change_name"
    )
    change_language = InlineKeyboardButton(
        text=buttons["change_language"], callback_data="change_language"
    )
    lk = InlineKeyboardButton(text=buttons["lk"], callback_data="profile")

    keyboard = [[change_firstname], [change_language], [lk]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


# Список ачивок
def pagination_keyboard(
    buttons_count: int,
    start: int = 0,
    end: int = 5,
    cd: str = "data",
    page_size: int = 5,
    extra_button: dict = None,
) -> InlineKeyboardMarkup:
    """Функция для генерации кнопок с номерами элементов."""
    keyboard = []
    buttons = []
    nav_buttons = []
    button_next = InlineKeyboardButton(text=">>", callback_data=f"{cd}:next")
    button_prev = InlineKeyboardButton(
        text="<<", callback_data=f"{cd}:previous"
    )
    info_button = InlineKeyboardButton(
        text=f"{end}/{buttons_count}", callback_data=f"{cd}:info"
    )
    for i in range(buttons_count):
        buttons.append(
            InlineKeyboardButton(
                text=f"{i + 1}", callback_data=f"{cd}:{i + 1}"
            )
        )
    keyboard.append(buttons[start:end])
    if buttons_count > page_size:
        nav_buttons.append(button_prev)
        nav_buttons.append(info_button)
        nav_buttons.append(button_next)
    if nav_buttons:
        keyboard.append(nav_buttons)
    if extra_button:
        keyboard.append([InlineKeyboardButton(**extra_button)])
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


# Отдельная ачивка
def task_keyboard(
    language: str, show_tasks: bool = True
) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру с кнопками в отдельной ачивке."""
    buttons = BUTTONS[language]
    lk = InlineKeyboardButton(text=buttons["lk"], callback_data="profile")
    available_achievements = {
        "text": buttons["available_achievements"],
        "callback_data": "available_achievements",
    }
    back_to_achievements = {
        "text": buttons["back"],
        "callback_data": "back_to_available_achievements",
    }
    tasks = (
        InlineKeyboardButton(**available_achievements)
        if show_tasks
        else InlineKeyboardButton(**back_to_achievements)
    )
    keyboard = [[tasks], [lk]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


def task_page_keyboard(
    language: str, available: bool = True
) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру с кнопками в отдельной ачивке."""
    buttons = BUTTONS[language]
    lk = InlineKeyboardButton(text=buttons["lk"], callback_data="profile")
    back_to_achievements = {
        "text": buttons["back"],
        "callback_data": "back_to_available_achievements",
    }
    fulfil_achievement = InlineKeyboardButton(
        text=buttons["fulfil_achievement"], callback_data="fulfil_achievement"
    )
    keyboard = [[back_to_achievements], [lk]]
    if available:
        keyboard = [[fulfil_achievement], [back_to_achievements], [lk]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


def send_artifact_keyboard(language: str, cd: str):
    """Генерирует клавиатуру на странице отправки артефактов."""
    buttons = BUTTONS[language]
    lk = InlineKeyboardButton(text=buttons["lk"], callback_data="profile")
    back_to_achievement = {
        "text": buttons["back"],
        "callback_data": f"back_to_chosen_achievement:{cd}",
    }
    keyboard = [[back_to_achievement], [lk]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


# Написать вожатому
def contacts_keyboard(language: str, username: str) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру для связи с вожатым."""
    buttons = BUTTONS[language]
    counsellor_chat = InlineKeyboardButton(
        text=buttons["counsellor_chat"], url=f"https://t.me/{username}"
    )
    lk = InlineKeyboardButton(text=buttons["lk"], callback_data="profile")

    keyboard = [[counsellor_chat], [lk]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


# Клавиатура с кнопкой Личный кабинет
def help_keyboard(language: str) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру при нажатии команды help."""
    buttons = BUTTONS[language]
    lk = InlineKeyboardButton(text=buttons["lk"], callback_data="profile")
    keyboard = [[lk]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


def join_team_keyboard(language: str) -> InlineKeyboardMarkup:
    """Клавиатура ребенка для присоединения к команде."""
    buttons = BUTTONS[language]
    join = InlineKeyboardButton(
        text=buttons["join_team"], callback_data="join_team"
    )
    back_to_team_list = InlineKeyboardButton(
        text=buttons["back"], callback_data="back_to_team_list"
    )
    lk = InlineKeyboardButton(text=buttons["lk"], callback_data="profile")
    keyboard = [[join], [back_to_team_list], [lk]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


def become_cap_or_leave_team_keyboard(
    language: str, cap_pos_available: bool = False
) -> InlineKeyboardMarkup:
    """Клавиатура ребенка: уйти из команды или стать капитаном."""
    buttons = BUTTONS[language]
    leave = InlineKeyboardButton(
        text=buttons["leave_team"], callback_data="leave_team"
    )
    back_to_team_list = InlineKeyboardButton(
        text=buttons["back"], callback_data="back_to_team_list"
    )
    lk = InlineKeyboardButton(text=buttons["lk"], callback_data="profile")
    keyboard = [[leave], [back_to_team_list], [lk]]
    if cap_pos_available:
        become_captain = InlineKeyboardButton(
            text=buttons["become_captain"], callback_data="become_captain"
        )
        keyboard[0].append(become_captain)
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


def leave_captain_position_keyboard(language: str) -> InlineKeyboardMarkup:
    """Клавиатура ребенка для удаления c поста капитана команды."""
    buttons = BUTTONS[language]
    leave = InlineKeyboardButton(
        text=buttons["leave_team"], callback_data="leave_team"
    )
    leave_cap_pos = InlineKeyboardButton(
        text=buttons["leave_captain_position"],
        callback_data="leave_captain_position",
    )
    back_to_team_list = InlineKeyboardButton(
        text=buttons["back"], callback_data="back_to_team_list"
    )
    lk = InlineKeyboardButton(text=buttons["lk"], callback_data="profile")
    keyboard = [[leave], [leave_cap_pos], [back_to_team_list], [lk]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


def team_full_keyboard(language: str) -> InlineKeyboardMarkup:
    """Клавиатура ребенка, если в команде нет мест."""
    buttons = BUTTONS[language]
    back_to_team_list = InlineKeyboardButton(
        text=buttons["back"], callback_data="back_to_team_list"
    )
    lk = InlineKeyboardButton(text=buttons["lk"], callback_data="profile")
    keyboard = [[back_to_team_list], [lk]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup


def cancel_keyboard(language: str) -> InlineKeyboardMarkup:
    buttons = BUTTONS[language]
    cancel_button: InlineKeyboardButton = InlineKeyboardButton(
        text=buttons["cancel"], callback_data="cancel"
    )
    cancel: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[cancel_button]]
    )
    return cancel


def yes_no_keyboard(language: str, cd: str) -> InlineKeyboardMarkup:
    buttons = BUTTONS[language]
    yes_button = InlineKeyboardButton(
        text=buttons["yes"], callback_data=f"yes:{cd}"
    )
    no_button = InlineKeyboardButton(
        text=buttons["no"], callback_data=f"no:{cd}"
    )
    return InlineKeyboardMarkup(inline_keyboard=[[yes_button], [no_button]])


# Список ачивок
def pagination_keyboard_category(
    buttons_count: int,
    start: int = 0,
    end: int = 5,
    cd: str = "categories",
    page_size: int = 5,
    extra_button: dict = None,
) -> InlineKeyboardMarkup:
    """Функция для генерации кнопок с номерами элементов."""
    keyboard = []
    buttons = []
    nav_buttons = []
    button_next = InlineKeyboardButton(text=">>", callback_data=f"{cd}:next")
    button_prev = InlineKeyboardButton(
        text="<<", callback_data=f"{cd}:previous"
    )
    info_button = InlineKeyboardButton(
        text=f"{end}/{buttons_count}", callback_data=f"{cd}:info"
    )
    keyboard.append(buttons[start:end])
    if buttons_count > page_size:
        nav_buttons.append(button_prev)
        nav_buttons.append(info_button)
        nav_buttons.append(button_next)
    if nav_buttons:
        keyboard.append(nav_buttons)
    if extra_button:
        keyboard.append([InlineKeyboardButton(**extra_button)])
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup

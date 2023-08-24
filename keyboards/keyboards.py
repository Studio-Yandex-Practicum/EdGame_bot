from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


# Функция, генерирующая клавиатуру для выбора языка
def create_welcome_keyboard():
    # Создаем объекты инлайн-кнопок
    rus_lang: InlineKeyboardButton = InlineKeyboardButton(
        text="Русский язык", callback_data="ru_pressed"
    )
    tatar_lang: InlineKeyboardButton = InlineKeyboardButton(
        text="Татар теле", callback_data="tt_pressed"
    )
    eng_lang: InlineKeyboardButton = InlineKeyboardButton(
        text="English language", callback_data="en_pressed"
    )
    # Создаем объект инлайн-клавиатуры
    welcome_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[rus_lang], [tatar_lang], [eng_lang]]
    )
    return welcome_keyboard


# Текст на кнопках

# Главное меню
profile = KeyboardButton(text="Личный кабинет")
show_tasks = KeyboardButton(text="Посмотреть доступные ачивки")
teacher_feedback = KeyboardButton(text="Посмотреть проверенные ачивки")

menu_keyboard = [[show_tasks], [teacher_feedback], [profile]]


# Личный кабинет
edit_profile = KeyboardButton(text="Редактировать профиль")
write_to_methodist = KeyboardButton(text="Написать преподавателю")

profile_keyboard = [[edit_profile], [write_to_methodist]]

# Кнопки inline

# Выбор языка
russian = InlineKeyboardButton(text="Русский", callback_data="russian")
tatar = InlineKeyboardButton(text="Татарский", callback_data="tatar")
english = InlineKeyboardButton(text="Английский", callback_data="english")

choose_language_keyboard = [[russian], [tatar], [english]]

# Редактирование профиля
change_firstname = InlineKeyboardButton(text="Имя", callback_data="change_name")
change_language = InlineKeyboardButton(
    text="Язык бота", callback_data="change_language"
)
change_bio = InlineKeyboardButton(text="Информацию о себе", callback_data="change_bio")

edit_profile_keyboard = [[change_firstname], [change_language], [change_bio]]

# Список ачивок
one = InlineKeyboardButton(text="1", callback_data="1")
two = InlineKeyboardButton(text="2", callback_data="2")
three = InlineKeyboardButton(text="3", callback_data="3")
four = InlineKeyboardButton(text="4", callback_data="4")
five = InlineKeyboardButton(text="5", callback_data="5")
six = InlineKeyboardButton(text="6", callback_data="6")
seven = InlineKeyboardButton(text="7", callback_data="7")

task_list_keyboard = {
    1: [[one]],
    2: [[one, two]],
    3: [[one, two, three]],
    4: [[one, two, three, four]],
    5: [[one, two, three, four, five]],
    6: [[one, two, three, four, five, six]],
    7: [[one, two, three, four, five, six, seven]],
}

# Отдельная ачивка
main_menu = InlineKeyboardButton(text="Главное меню", callback_data="main_menu")
task_list = InlineKeyboardButton(
    text="Посмотреть доступные ачивки", callback_data="show_tasks_list"
)

task_keyboard = [[task_list], [main_menu]]


# Создание клавиатуры для ЛК вожатого
def create_profile_keyboard():
    profile_keyboard = [
        [KeyboardButton(text="Список детей")],
        [KeyboardButton(text="Проверить задания")],
    ]
    return ReplyKeyboardMarkup(keyboard=profile_keyboard, resize_keyboard=True)


# Создание инлайн клавиатуры для проверки задания вожатым
def create_inline_keyboard(task_id):
    accept_button = InlineKeyboardButton(
        text="✔️ Принять", callback_data=f"accept:{task_id}"
    )

    reject_button = InlineKeyboardButton(
        text="❌ Отклонить", callback_data=f"reject:{task_id}"
    )
    send_back_button = InlineKeyboardButton(
        text="🔄 Отправить на доп.проверку", callback_data=f"back:{task_id}"
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[[accept_button], [reject_button], [send_back_button]]
    )


# Создание инлайн клавиатуры для добавления комментария при отколении вожатым дз
def create_yes_no_keyboard(task_id):
    yes_button = InlineKeyboardButton(text="Да", callback_data=f"yes:{task_id}")
    no_button = InlineKeyboardButton(text="Нет", callback_data=f"no:{task_id}")
    return InlineKeyboardMarkup(inline_keyboard=[[yes_button], [no_button]])

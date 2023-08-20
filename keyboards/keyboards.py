from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton)

from lexicon.lexicon import BUTTONS


# Функция, генерирующая клавиатуру для выбора языка
def create_welcome_keyboard():
    # Создаем объекты инлайн-кнопок
    rus_lang: InlineKeyboardButton = InlineKeyboardButton(
        text='Русский язык',
        callback_data='ru_pressed')
    tatar_lang: InlineKeyboardButton = InlineKeyboardButton(
        text='Татар теле',
        callback_data='tt_pressed')
    eng_lang: InlineKeyboardButton = InlineKeyboardButton(
        text='English language',
        callback_data='en_pressed')
    # Создаем объект инлайн-клавиатуры
    welcome_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[rus_lang],
                         [tatar_lang],
                         [eng_lang]])
    return welcome_keyboard


# Текст на кнопках
# Главное меню
def menu_keyboard(language):
    '''Генерирует клавиатуру с кнопками в главном меню.'''
    buttons = BUTTONS[language]
    write_to_methodist = KeyboardButton(text=buttons["write_to_methodist"])
    lk = KeyboardButton(text=buttons["lk"])
    help_button = KeyboardButton(text=buttons["help"])

    keyboard = [
        [lk],
        [help_button],
        [write_to_methodist]]
    return keyboard


# Личный кабинет
def profile_keyboard(language):
    '''Генерирует клавиатуру с кнопками в личном кабинете.'''
    buttons = BUTTONS[language]
    edit_profile = KeyboardButton(text=buttons["edit_profile"])
    available_achievements = KeyboardButton(
        text=buttons["available_achievements"])
    current_achievements = KeyboardButton(text=buttons["current_achievements"])
    reviewed_achievements = KeyboardButton(
        text=buttons["reviewed_achievements"])
    write_to_councelor = KeyboardButton(text=buttons["write_to_councelor"])
    keyboard = [
        [available_achievements, current_achievements],
        [reviewed_achievements],
        [edit_profile, write_to_councelor]]
    return keyboard


# Кнопки inline

# Выбор языка
russian = InlineKeyboardButton(text='Русский язык', callback_data='RU')
tatar = InlineKeyboardButton(text='Татар теле', callback_data='TT')
english = InlineKeyboardButton(text='English language', callback_data='EN')

choose_language_keyboard = [
    [russian],
    [tatar],
    [english]
]


# Редактирование профиля
def edit_profile_keyboard(language: str):
    '''Генерирует клавиатуру с кнопками в редактировании профиля.'''
    buttons = BUTTONS[language]
    change_firstname = InlineKeyboardButton(
        text=buttons["change_firstname"], callback_data='change_name')
    change_language = InlineKeyboardButton(
        text=buttons["change_language"], callback_data='change_language')

    keyboard = [
        [change_firstname],
        [change_language]]
    return keyboard


# Список ачивок
def task_list_keyboard(buttons_count: int, start: int = 0, end: int = 5):
    '''Функция для генерации кнопок с номерами ачивок.'''
    keyboard = []
    buttons = []
    nav_buttons = []
    button_next = InlineKeyboardButton(text='>>', callback_data='next')
    button_prev = InlineKeyboardButton(text='<<', callback_data='previous')
    info_button = InlineKeyboardButton(
        text=f'{end}/{buttons_count}', callback_data='info')
    for i in range(buttons_count):
        buttons.append(InlineKeyboardButton(
            text=f'{i + 1}', callback_data=f'{i + 1}'))
    keyboard.append(buttons[start:end])
    if start > 0 and buttons_count > end:
        nav_buttons.append(button_prev)
        nav_buttons.append(info_button)
        nav_buttons.append(button_next)
    elif buttons_count > end:
        nav_buttons.append(info_button)
        nav_buttons.append(button_next)
    elif start > 0:
        nav_buttons.append(button_prev)
        nav_buttons.append(info_button)
    if nav_buttons:
        keyboard.append(nav_buttons)
    return keyboard


# Отдельная ачивка
def task_keyboard(language: str):
    '''Генерирует клавиатуру с кнопками в отдельной ачивке.'''
    buttons = BUTTONS[language]
    lk = InlineKeyboardButton(
        text=buttons["lk"], callback_data='profile')
    available_achievements = InlineKeyboardButton(
        text=buttons["available_achievements"],
        callback_data='available_achievements')

    keyboard = [
        [available_achievements],
        [lk]]
    return keyboard


# Написать вожатому
def contacts_keyboard(language, username):
    '''Генерирует клавиатуру для связи с вожатым.'''
    buttons = BUTTONS[language]
    councelor_chat = InlineKeyboardButton(
        text=buttons["councelor_chat"], url=f'https://t.me/{username}')
    lk = InlineKeyboardButton(
        text=buttons["lk"], callback_data='profile')

    keyboard = [
        [councelor_chat],
        [lk]]
    return keyboard


# Клавиатура с кнопкой Личный кабинет
def help_keyboard(language):
    '''Генерирует клавиатуру при нажатии команды help.'''
    buttons = BUTTONS[language]
    lk = InlineKeyboardButton(
        text=buttons["lk"], callback_data='profile')
    keyboard = [[lk]]
    return keyboard

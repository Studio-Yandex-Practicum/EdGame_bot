from aiogram.types import InlineKeyboardButton, KeyboardButton

from lexicon.lexicon import BUTTONS, LEXICON


# Кнопки при уведомлении о поступивших артефактах
def art_list_keyboard(language: str):
    '''Кнопки при входящем уведомлении методисту.'''
    buttons = BUTTONS[language]
    show_art_list = KeyboardButton(text=buttons["tasks_for_review"])
    lk = KeyboardButton(text=buttons["lk"])

    keyboard = [[show_art_list], [lk]]
    return keyboard


# Кнопки в личном кабинете
def methodist_profile_keyboard(language: str):
    '''Генерирует клавиатуру в ЛК методиста.'''
    buttons = BUTTONS[language]
    add_task = KeyboardButton(text=buttons["add_task"])
    achievement_list = KeyboardButton(text=buttons["achievement_list"])
    tasks_for_review = KeyboardButton(text=buttons["tasks_for_review"])
    edit_profile = KeyboardButton(text=buttons["edit_profile"])

    keyboard = [
        [add_task],
        [achievement_list],
        [tasks_for_review],
        [edit_profile]
    ]
    return keyboard


def add_task_keyboard(language: str):
    '''Генерирует инлайн клавиатуру в разделе добавления задания.'''
    buttons = BUTTONS[language]
    ready = InlineKeyboardButton(text=buttons["ready"], callback_data='ready')
    lk = InlineKeyboardButton(
        text=buttons["lk"], callback_data='profile')
    keyboard = [[ready], [lk]]
    return keyboard


def task_type_keyboard(language: str):
    '''Генерирует клавиатуру при выборе типа ачивки.'''
    buttons = LEXICON[language]
    individual = InlineKeyboardButton(
        text=buttons["individual"], callback_data='individual')
    teamwork = InlineKeyboardButton(
        text=buttons["teamwork"], callback_data='teamwork')
    keyboard = [[individual, teamwork]]
    return keyboard


def artifact_type_keyboard(language: str):
    '''Генерирует клавиатуру при выборе типа артефакта.'''
    buttons = LEXICON[language]
    text = InlineKeyboardButton(
        text=buttons["text"], callback_data='text')
    image = InlineKeyboardButton(
        text=buttons["image"], callback_data='image')
    video = InlineKeyboardButton(
        text=buttons["video"], callback_data='video')
    keyboard = [[text, image, video]]
    return keyboard


def confirm_task_keyboard(language: str):
    '''Генерирует клавиатуру при подтверждении добавления задания.'''
    buttons = BUTTONS[language]
    confirm_adding_task = InlineKeyboardButton(
        text=buttons["confirm_adding_task"], callback_data='confirm')
    edit_task = InlineKeyboardButton(
        text=buttons["edit_task"], callback_data='edit_task')
    keyboard = [[confirm_adding_task, edit_task]]
    return keyboard


def edit_task_keyboard(language: str):
    '''Генерирует клавиатуру в разделе редактирования заявки.'''
    buttons = BUTTONS[language]
    name = InlineKeyboardButton(
        text=buttons["edit_name"], callback_data='edit_name')
    image = InlineKeyboardButton(
        text=buttons["edit_image"], callback_data='edit_image')
    description = InlineKeyboardButton(
        text=buttons["edit_description"], callback_data='edit_description')
    instruction = InlineKeyboardButton(
        text=buttons["edit_instruction"], callback_data="edit_instruction")
    task_type = InlineKeyboardButton(
        text=buttons["edit_task_type"], callback_data='edit_task_type')
    artifact_type = InlineKeyboardButton(
        text=buttons["edit_artifact_type"], callback_data='edit_artifact_type')
    score = InlineKeyboardButton(
        text=buttons["edit_score"], callback_data='edit_score')
    price = InlineKeyboardButton(
        text=buttons["edit_price"], callback_data='edit_price')
    complete = InlineKeyboardButton(
        text=buttons["complete_editing_task"],
        callback_data='complete_editing')
    keyboard = [
        [name, image],
        [description, instruction],
        [task_type, artifact_type],
        [score, price],
        [complete]
    ]
    return keyboard


def task_keyboard_methodist(language: str):
    '''Генерирует клавиатуру с кнопками в отдельной ачивке.'''
    buttons = BUTTONS[language]
    lk = InlineKeyboardButton(
        text=buttons["lk"], callback_data='profile')
    achievement_list = InlineKeyboardButton(
        text=buttons["achievement_list"],
        callback_data='achievement_list')
    edit_task = InlineKeyboardButton(
        text=buttons["edit_task"], callback_data='edit_task')
    keyboard = [
        [edit_task],
        [achievement_list],
        [lk]]
    return keyboard

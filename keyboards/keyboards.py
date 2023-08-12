from aiogram.types import KeyboardButton, InlineKeyboardButton

# Текст на кнопках

back = KeyboardButton(text='Назад')
forward = KeyboardButton(text='Вперед')

# Главное меню
profile = KeyboardButton(text='Личный кабинет')
show_tasks = KeyboardButton(text='Посмотреть доступные ачивки')
teacher_feedback = KeyboardButton(text='Посмотреть проверенные ачивки')

menu_keyboard = [
    [show_tasks],
    [teacher_feedback],
    [profile]
]


# Личный кабинет
edit_profile = KeyboardButton(text='Редактировать профиль')

profile_keyboard = [
    [edit_profile],
    [back]
]

# Кнопки inline

# Кнопки да, нет
letsgo = InlineKeyboardButton(text='А давай', callback_data='letsgo')
later = InlineKeyboardButton(text='Может позже..', callback_data='later')
yes = InlineKeyboardButton(text='Да', callback_data='yes')
no = InlineKeyboardButton(text='Нет', callback_data='no')
already_registered = InlineKeyboardButton(
    text='Я уже зарегистрирован', callback_data='already_registered')

letsgo_keyboard = [
    [letsgo, later]
]
yes_keyboard = [
    [yes, no]
]
registered_keyboard = [[already_registered]]

# Выбор языка
russian = InlineKeyboardButton(text='Русский', callback_data='russian')
tatar = InlineKeyboardButton(text='Татарский', callback_data='tatar')
english = InlineKeyboardButton(text='Английский', callback_data='english')

choose_language_keyboard = [
    [russian],
    [tatar],
    [english]
]

# Редактирование профиля
change_firstname = InlineKeyboardButton(
    text='Имя', callback_data='change_firstname')
change_lastname = InlineKeyboardButton(
    text='Фамилию', callback_data='change_lastname')
change_photo = InlineKeyboardButton(
    text='Фото', callback_data='change_photo')
change_bio = InlineKeyboardButton(
    text='Информацию о себе', callback_data='change_bio')

edit_profile_keyboard = [
    [change_firstname],
    [change_lastname],
    [change_photo],
    [change_bio]
]

# Список ачивок
one = InlineKeyboardButton(text='1', callback_data='1')
two = InlineKeyboardButton(text='2', callback_data='2')
three = InlineKeyboardButton(text='3', callback_data='3')
four = InlineKeyboardButton(text='4', callback_data='4')

task_list_keyboard = [
    [one, two, three, four]
]

# Отдельная ачивка
main_menu = InlineKeyboardButton(
    text='Главное меню', callback_data='main_menu')
task_list = InlineKeyboardButton(
    text='Посмотреть доступные ачивки', callback_data='show_tasks_list')

task_keyboard = [
    [task_list],
    [main_menu]
]

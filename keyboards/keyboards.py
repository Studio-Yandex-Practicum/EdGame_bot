from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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

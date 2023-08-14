from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from lexicon.lexicon import LEXICON_RU


# Функция, генерирующая клавиатуру для выбора языка
def create_welcome_keyboard():
    # Создаем объекты инлайн-кнопок
    rus_lang: InlineKeyboardButton = InlineKeyboardButton(
        text='Русский язык',
        callback_data='rus_lang_pressed')
    tatar_lang: InlineKeyboardButton = InlineKeyboardButton(
        text='Татар теле',
        callback_data='tatar_lang_pressed')
    eng_lang: InlineKeyboardButton = InlineKeyboardButton(
        text='English language',
        callback_data='eng_lang_pressed')
    # Создаем объект инлайн-клавиатуры
    welcome_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[rus_lang],
                         [tatar_lang],
                         [eng_lang]])
    # Возвращаем объект инлайн-клавиатуры
    return welcome_keyboard

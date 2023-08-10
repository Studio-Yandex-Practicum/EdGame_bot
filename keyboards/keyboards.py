from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

button_1 = InlineKeyboardButton(text='Представиться',
                                callback_data='Будем знакомы.')

welcome_kb = InlineKeyboardMarkup(inline_keyboard=[[button_1]])

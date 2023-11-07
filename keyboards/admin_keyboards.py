from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def henchman_pass_keyboard():
    counselor_pass: InlineKeyboardButton = InlineKeyboardButton(
        text="Сменить пароль для вожатых", callback_data="counselor_pass"
    )
    methodist_pass: InlineKeyboardButton = InlineKeyboardButton(
        text="Сменить пароль для методистов", callback_data="methodist_pass"
    )
    henchman_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[counselor_pass], [methodist_pass]]
    )
    return henchman_keyboard


def boss_pass_keyboard():
    master_pass: InlineKeyboardButton = InlineKeyboardButton(
        text="Сменить мастер-пароль", callback_data="master_pass"
    )
    counselor_pass: InlineKeyboardButton = InlineKeyboardButton(
        text="Сменить пароль для вожатых", callback_data="counselor_pass"
    )
    methodist_pass: InlineKeyboardButton = InlineKeyboardButton(
        text="Сменить пароль для методистов", callback_data="methodist_pass"
    )
    boss_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[master_pass], [counselor_pass], [methodist_pass]]
    )
    return boss_keyboard

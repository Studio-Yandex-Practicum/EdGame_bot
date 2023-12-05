from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def henchman_pass_keyboard():
    kid_pass: InlineKeyboardButton = InlineKeyboardButton(
        text="Сменить пароль для студентов", callback_data="kid_pass"
    )
    counsellor_pass: InlineKeyboardButton = InlineKeyboardButton(
        text="Сменить пароль для вожатых", callback_data="counsellor_pass"
    )
    methodist_pass: InlineKeyboardButton = InlineKeyboardButton(
        text="Сменить пароль для методистов", callback_data="methodist_pass"
    )
    henchman_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[kid_pass], [counsellor_pass], [methodist_pass]]
    )
    return henchman_keyboard


def boss_pass_keyboard():
    kid_pass: InlineKeyboardButton = InlineKeyboardButton(
        text="Сменить пароль для студентов", callback_data="kid_pass"
    )
    counsellor_pass: InlineKeyboardButton = InlineKeyboardButton(
        text="Сменить пароль для вожатых", callback_data="counsellor_pass"
    )
    methodist_pass: InlineKeyboardButton = InlineKeyboardButton(
        text="Сменить пароль для методистов", callback_data="methodist_pass"
    )
    master_pass: InlineKeyboardButton = InlineKeyboardButton(
        text="Сменить мастер-пароль", callback_data="master_pass"
    )
    boss_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[
            [kid_pass],
            [counsellor_pass],
            [methodist_pass],
            [master_pass],
        ]
    )
    return boss_keyboard

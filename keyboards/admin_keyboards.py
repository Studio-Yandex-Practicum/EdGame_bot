from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.orm import Session

from db.models import Season
from lexicon.lexicon import BUTTONS


def henchman_pass_keyboard(session: Session, language: str):
    buttons = BUTTONS[language]
    kid_pass: InlineKeyboardButton = InlineKeyboardButton(
        text=buttons["change_pass_student"], callback_data="kid_pass"
    )
    counsellor_pass: InlineKeyboardButton = InlineKeyboardButton(
        text=buttons["change_pass_counsellor"], callback_data="counsellor_pass"
    )
    methodist_pass: InlineKeyboardButton = InlineKeyboardButton(
        text=buttons["change_pass_methodist"], callback_data="methodist_pass"
    )
    open_season: InlineKeyboardButton = InlineKeyboardButton(
        text=buttons["open_season"], callback_data="open_season"
    )
    close_season: InlineKeyboardButton = InlineKeyboardButton(
        text=buttons["close_season"], callback_data="close_season"
    )
    export_xls: InlineKeyboardButton = InlineKeyboardButton(
        text=buttons["export_xls"], callback_data="export_xls"
    )

    season_now = session.query(Season).first()
    if season_now:
        season = close_season
    else:
        season = open_season

    henchman_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[
            [kid_pass],
            [counsellor_pass],
            [methodist_pass],
            [export_xls],
            [season],
        ]
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

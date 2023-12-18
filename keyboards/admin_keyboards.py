from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.engine import Session
from db.models import Season, User


def henchman_pass_keyboard(session):
    kid_pass: InlineKeyboardButton = InlineKeyboardButton(
        text="Сменить пароль для студентов", callback_data="kid_pass"
    )
    counsellor_pass: InlineKeyboardButton = InlineKeyboardButton(
        text="Сменить пароль для вожатых", callback_data="counsellor_pass"
    )
    methodist_pass: InlineKeyboardButton = InlineKeyboardButton(
        text="Сменить пароль для методистов", callback_data="methodist_pass"
    )
    open_season: InlineKeyboardButton = InlineKeyboardButton(
        text="Открыть сезон", callback_data="open_season"
    )
    close_season: InlineKeyboardButton = InlineKeyboardButton(
        text="Закрыть сезон", callback_data="close_season"
    )
    export_xls: InlineKeyboardButton = InlineKeyboardButton(
        text="Экспорт в excel", callback_data="export_xls"
    )
    user_delete: InlineKeyboardButton = InlineKeyboardButton(
        text="Удалить пользователя", callback_data="user_del"
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
            [user_delete],
            [export_xls],
            [season],
        ]
    )
    return henchman_keyboard


def henchman_user_del_keyboard():
    kid_del: InlineKeyboardButton = InlineKeyboardButton(
        text="Удалить ребенка", callback_data="kid_del"
    )
    counsellor_del: InlineKeyboardButton = InlineKeyboardButton(
        text="Удалить вожатого", callback_data="counsellor_del"
    )
    methodist_del: InlineKeyboardButton = InlineKeyboardButton(
        text="Удалить методиста", callback_data="methodist_del"
    )
    back: InlineKeyboardButton = InlineKeyboardButton(
        text="Назад", callback_data="back_del"
    )
    del_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[
            [kid_del],
            [counsellor_del],
            [methodist_del],
            [back],
        ]
    )
    return del_keyboard


def kid_del_keyboard():
    session = Session()
    kb_builder = InlineKeyboardBuilder()
    kids = session.query(User).filter_by(role="kid").all()
    for kid in kids:
        kb_builder.row(
            InlineKeyboardButton(
                text=f"{kid.name} - {kid.id}", callback_data=f"{kid.id}_del"
            )
        )
    kb_builder.row(
        InlineKeyboardButton(text="Назад", callback_data="back_del")
    )
    return kb_builder.as_markup()


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

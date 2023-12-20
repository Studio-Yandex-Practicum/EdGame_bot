from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.models import Season, User
from lexicon.lexicon import BUTTONS, LEXICON
from utils.db_commands import select_user


def henchman_pass_keyboard(session):
    """Клавиатура админа."""
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


def henchman_user_del_keyboard(session, callback):
    """Клавиатура удаления пользователя."""
    user = select_user(session, callback.message.chat.id)

    kid_del: InlineKeyboardButton = InlineKeyboardButton(
        text=LEXICON[user.language]["kid_del"], callback_data="kid_del"
    )
    counsellor_del: InlineKeyboardButton = InlineKeyboardButton(
        text=LEXICON[user.language]["counsellor_del"],
        callback_data="counsellor_del",
    )
    methodist_del: InlineKeyboardButton = InlineKeyboardButton(
        text=LEXICON[user.language]["methodist_del"],
        callback_data="methodist_del",
    )
    back: InlineKeyboardButton = InlineKeyboardButton(
        text=BUTTONS[user.language]["back"], callback_data="back_del"
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


def kid_del_keyboard(session, callback):
    """Клавиатура-список детей для удаления."""
    user = select_user(session, callback.message.chat.id)

    kb_builder = InlineKeyboardBuilder()
    kids = session.query(User).filter_by(role="kid").all()
    for kid in kids:
        kb_builder.row(
            InlineKeyboardButton(
                text=f"{kid.name} - {kid.id}", callback_data=f"{kid.id}_del"
            )
        )
    kb_builder.row(
        InlineKeyboardButton(
            text=BUTTONS[user.language]["back"], callback_data="back_del"
        )
    )
    return kb_builder.as_markup()


def counsellor_del_keyboard(session, callback):
    """Клавиатура-список вожатых для удаления."""
    user = select_user(session, callback.message.chat.id)

    kb_builder = InlineKeyboardBuilder()
    counsellors = session.query(User).filter_by(role="counsellor").all()
    for counsellor in counsellors:
        kb_builder.row(
            InlineKeyboardButton(
                text=f"{counsellor.name} - {counsellor.id}",
                callback_data=f"{counsellor.id}_del",
            )
        )
    kb_builder.row(
        InlineKeyboardButton(
            text=BUTTONS[user.language]["back"], callback_data="back_del"
        )
    )
    return kb_builder.as_markup()


def methodist_del_keyboard(session, callback):
    """Клавиатура-список методистов для удаления."""
    user = select_user(session, callback.message.chat.id)

    kb_builder = InlineKeyboardBuilder()
    methodists = session.query(User).filter_by(role="methodist").all()
    for methodist in methodists:
        kb_builder.row(
            InlineKeyboardButton(
                text=f"{methodist.name} - {methodist.id}",
                callback_data=f"{methodist.id}_del",
            )
        )
    kb_builder.row(
        InlineKeyboardButton(
            text=BUTTONS[user.language]["back"], callback_data="back_del"
        )
    )
    return kb_builder.as_markup()


def boss_pass_keyboard():
    """Клавиатура босса."""
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

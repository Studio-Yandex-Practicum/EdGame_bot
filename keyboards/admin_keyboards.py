from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from db.models import Season
from lexicon.lexicon import BUTTONS, LEXICON
from utils.db_commands import get_users_by_role, select_user


def henchman_pass_keyboard(session: Session, language: str):
    """Клавиатура админа."""
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


def user_del_keyboard(session, role, callback):
    """Клавиатура-список для удаления."""
    user = select_user(session, callback.message.chat.id)
    user_role2del = get_users_by_role(session, role=role)

    kb_builder = InlineKeyboardBuilder()
    for user in user_role2del:
        kb_builder.row(
            InlineKeyboardButton(
                text=f"{user.name} - {user.id}", callback_data=f"{user.id}_del"
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
    delete_admin = InlineKeyboardButton(
        text="Удалить администратора", callback_data="show_admins"
    )
    boss_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[
            [kid_pass],
            [counsellor_pass],
            [methodist_pass],
            [master_pass],
            [delete_admin],
        ]
    )
    return boss_keyboard


async def multiselect_kb(data: dict, language: str, back_btn_cd: str):
    """Клавиатура с множественным выбором.

    :data - {22442: {"name": name, "checked": False}}
    """
    kb = InlineKeyboardBuilder()
    for user_id, params in data.items():
        if params["selected"]:
            kb.row(
                InlineKeyboardButton(
                    text=f"✓ {params['name']} ({user_id})",
                    callback_data=f"{user_id}_collapse",
                )
            )
        else:
            kb.row(
                InlineKeyboardButton(
                    text=f"{params['name']} ({user_id})",
                    callback_data=f"{user_id}_extend",
                )
            )
    kb.adjust(2)
    kb.row(
        InlineKeyboardButton(
            text=BUTTONS[language]["back"], callback_data=back_btn_cd
        ),
        InlineKeyboardButton(
            text=BUTTONS[language]["delete"], callback_data="delete_users"
        ),
    )
    return kb.as_markup()

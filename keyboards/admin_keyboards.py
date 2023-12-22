from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.models import Season
from lexicon.lexicon import BUTTONS


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

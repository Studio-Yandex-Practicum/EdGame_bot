import datetime
import hashlib
import logging
import os
import re
import shutil
from typing import Any, Callable

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from aiogram.types.input_file import FSInputFile
from sqlalchemy.orm import Session

from config_data.config import load_config
from db.models import Password, Season, User
from keyboards.admin_keyboards import (
    boss_pass_keyboard,
    henchman_pass_keyboard,
    henchman_user_del_keyboard,
    multiselect_kb,
    user_del_keyboard,
)
from keyboards.keyboards import cancel_keyboard, yes_no_keyboard
from lexicon.lexicon import LEXICON
from utils.db_commands import get_users_by_role, select_user, users_deleting
from utils.states_form import (
    CounsellorPassword,
    KidPassword,
    MasterPassword,
    MethodistPassword,
    UserDel,
)
from utils.user_utils import (
    delete_bd,
    foto_user_id,
    statistics,
    text_files,
    zip_files,
)
from utils.utils import data_for_multiselect_kb

admin_router = Router()
config = load_config()
logger = logging.getLogger(__name__)


@admin_router.callback_query(F.data == "kid_pass", StateFilter(default_state))
async def change_kid_pass(
    callback: CallbackQuery, state: FSMContext, session: Session
):
    """Смена пароля ребенка."""
    user = select_user(session, callback.from_user.id)
    language = user.language
    await callback.message.delete()
    await callback.message.answer(
        text=LEXICON[language]["kid_pass"],
        reply_markup=cancel_keyboard(language)
    )
    await state.set_state(KidPassword.psw2hash)


# Обрабатываем пароль ребенка
@admin_router.message(StateFilter(KidPassword.psw2hash))
async def hashing_kid_password(
    message: Message, state: FSMContext, session: Session
):
    """Хешируем и сохраняем новый пароль ребенка."""
    user = select_user(session, message.chat.id)
    lexicon = LEXICON[user.language]
    psw_kid_hash = hashlib.sha256(message.text.encode())
    kid_psw = psw_kid_hash.hexdigest()
    session.query(Password).update({Password.kid_pass: kid_psw})
    await message.answer(text=lexicon["password_updated"])
    await state.clear()


@admin_router.callback_query(
    F.data == "counsellor_pass", StateFilter(default_state)
)
async def change_counsellor_pass(
    callback: CallbackQuery, state: FSMContext, session: Session
):
    """Смена пароля вожатого."""
    user = select_user(session, callback.from_user.id)
    language = user.language
    await callback.message.delete()
    await callback.message.answer(
        text=LEXICON[language]["counsellor_pass"],
        reply_markup=cancel_keyboard(language)
    )
    await state.set_state(CounsellorPassword.psw2hash)


# Обрабатываем пароль вожатого
@admin_router.message(StateFilter(CounsellorPassword.psw2hash))
async def hashing_counsellor_password(
    message: Message, state: FSMContext, session: Session
):
    """Хешируем и сохраняем новый пароль вожатого."""
    user = select_user(session, message.chat.id)
    lexicon = LEXICON[user.language]
    psw_counsellor_hash = hashlib.sha256(message.text.encode())
    counsellor_psw = psw_counsellor_hash.hexdigest()
    session.query(Password).update({Password.counsellor_pass: counsellor_psw})
    await message.answer(text=lexicon["password_updated"])
    await state.clear()


@admin_router.callback_query(
    F.data == "methodist_pass", StateFilter(default_state)
)
async def change_methodist_pass(
    callback: CallbackQuery, state: FSMContext, session: Session
):
    """Смена пароля методиста."""
    user = select_user(session, callback.from_user.id)
    language = user.language
    await callback.message.delete()
    await callback.message.answer(
        text=LEXICON[language]["methodist_pass"],
        reply_markup=cancel_keyboard(language)
    )
    await state.set_state(MethodistPassword.psw2hash)


# Обрабатываем пароль методиста
@admin_router.message(StateFilter(MethodistPassword.psw2hash))
async def hashing_methodist_password(
    message: Message, state: FSMContext, session: Session
):
    """Хешируем и сохраняем новый пароль методиста."""
    user = select_user(session, message.chat.id)
    lexicon = LEXICON[user.language]
    psw_methodist_hash = hashlib.sha256(message.text.encode())
    methodist_psw = psw_methodist_hash.hexdigest()
    session.query(Password).update({Password.methodist_pass: methodist_psw})
    await message.answer(text=lexicon["password_updated"])
    await state.clear()


@admin_router.callback_query(
    F.data == "master_pass", StateFilter(default_state)
)
async def change_master_pass(
    callback: CallbackQuery, state: FSMContext, session: Session
):
    """Смена мастер-пароля."""
    user = select_user(session, callback.from_user.id)
    language = user.language
    await callback.message.delete()
    await callback.message.answer(
        text=LEXICON[language]["master_pass"],
        reply_markup=cancel_keyboard(language)
    )
    await state.set_state(MasterPassword.psw2hash)


# Обрабатываем мастер-пароль
@admin_router.message(StateFilter(MasterPassword.psw2hash))
async def hashing_master_password(
    message: Message, state: FSMContext, session: Session
):
    """Хешируем и сохраняем новый мастер-пароль."""
    user = select_user(session, message.chat.id)
    lexicon = LEXICON[user.language]
    psw_master_hash = hashlib.sha256(message.text.encode())
    master_psw = psw_master_hash.hexdigest()
    session.query(Password).update({Password.master_pass: master_psw})
    await message.answer(text=lexicon["password_updated"])
    await state.clear()


@admin_router.callback_query(F.data == "cancel")
async def cancel_pass(
    callback: CallbackQuery, state: FSMContext, session: Session
):
    """Отмена ввода пароля."""
    if callback.message.chat.id == config.boss_id:
        await callback.message.edit_reply_markup(
            reply_markup=boss_pass_keyboard()
        )
    else:
        user = select_user(session, callback.from_user.id)
        language = user.language
        await callback.message.edit_reply_markup(
            reply_markup=henchman_pass_keyboard(session, language)
        )
    await state.clear()


@admin_router.callback_query(F.data == "open_season")
async def open_season(callback: CallbackQuery, session: Session):
    """Открываем сезон."""
    user = select_user(session, callback.from_user.id)
    language = user.language
    season = Season(
        open_season=datetime.datetime.now(),
    )
    session.add(season)
    session.commit()
    await callback.message.edit_reply_markup(
        text=LEXICON[language]["season_opened"],
        reply_markup=henchman_pass_keyboard(session, language)
    )


@admin_router.callback_query(F.data == "close_season")
async def close_season(callback: CallbackQuery, session: Session, bot):
    """Закрываем сезон."""
    user = select_user(session, callback.from_user.id)
    language = user.language
    season = session.query(Season).first()
    season.close_season = datetime.datetime.now()
    session.add(season)
    session.commit()
    try:
        await export_excel(callback, session, bot)
        delete_bd(session)
        await callback.message.answer(text=LEXICON[language]["season_closed"])
    except FileNotFoundError as err:
        logger.error(f"Файл не создан: {err}")
    except Exception as err:
        logger.error(f"Ошибка при выборе статистических данных: {err}")


@admin_router.callback_query(F.data == "export_xls")
async def export_excel(callback: CallbackQuery, session: Session, bot):
    """Экспорт в эксель."""
    try:
        statistics(session)
        text_files(session)
        files_id = foto_user_id(session)
        if files_id:
            for name, foto in files_id.items():
                j = 0
                for i in foto:
                    j += 1
                    file = await bot.get_file(i)
                    file_path = file.file_path
                    await bot.download_file(
                        file_path, f"./statictica//{name}//{name}, {j}"
                    )
        zip_files()
        file = "statictica.zip"
        await bot.send_document(callback.message.chat.id, FSInputFile(file))
    except FileNotFoundError as err:
        logger.error(f"Файл не создан: {err}")
    except Exception as err:
        logger.error(f"Ошибка при выборе статистических данных: {err}")
    finally:
        shutil.rmtree("statictica")
        os.remove("statictica.zip")
        await callback.message.delete()


@admin_router.callback_query(F.data == "user_del")
async def get_role2del(
    callback: CallbackQuery, state: FSMContext, session: Session
):
    """Выбор роли ребенка, вожатого или методиста."""
    await callback.message.delete()
    user = select_user(session, callback.message.chat.id)
    await callback.message.answer(
        LEXICON[user.language]["get_role2del"],
        reply_markup=henchman_user_del_keyboard(session, callback),
    )
    await state.set_state(UserDel.get_role)


@admin_router.callback_query(F.data == "back_del")
async def back_del(
    callback: CallbackQuery, state: FSMContext, session: Session
):
    """Вернуться назад."""
    user = select_user(session, callback.from_user.id)
    language = user.language
    await state.clear()
    await callback.message.edit_reply_markup(
        reply_markup=henchman_pass_keyboard(session, language)
    )


@admin_router.callback_query(
    F.data == "kid_del", StateFilter(UserDel.get_role)
)
async def get_kids(
    callback: CallbackQuery, state: FSMContext, session: Session
):
    """Вывод списка детей."""
    await callback.message.delete()
    user = select_user(session, callback.message.chat.id)
    role = "kid"
    await callback.message.answer(
        LEXICON[user.language]["select_kid"],
        reply_markup=user_del_keyboard(session, role, callback),
    )
    await state.set_state(UserDel.list_users)


@admin_router.callback_query(
    F.data == "counsellor_del", StateFilter(UserDel.get_role)
)
async def get_counsellors(
    callback: CallbackQuery, state: FSMContext, session: Session
):
    """Вывод списка вожатых."""
    await callback.message.delete()
    user = select_user(session, callback.message.chat.id)
    role = "counsellor"
    await callback.message.answer(
        LEXICON[user.language]["select_counsellor"],
        reply_markup=user_del_keyboard(session, role, callback),
    )
    await state.set_state(UserDel.list_users)


@admin_router.callback_query(
    F.data == "methodist_del", StateFilter(UserDel.get_role)
)
async def get_methodists(
    callback: CallbackQuery, state: FSMContext, session: Session
):
    """Вывод списка методистов."""
    await callback.message.delete()
    user = select_user(session, callback.message.chat.id)
    role = "methodist"
    await callback.message.answer(
        LEXICON[user.language]["select_methodist"],
        reply_markup=user_del_keyboard(session, role, callback),
    )
    await state.set_state(UserDel.list_users)


@admin_router.callback_query(
    F.data.endswith("_del"), StateFilter(UserDel.list_users)
)
async def del_kid(
    callback: CallbackQuery, state: FSMContext, session: Session
):
    """Удаление ребенка."""
    user = select_user(session, callback.from_user.id)
    language = user.language
    await callback.message.delete()
    user = select_user(session, callback.message.chat.id)
    user2del = session.query(User).filter_by(id=callback.data[:-4]).first()
    session.delete(user2del)
    await state.clear()
    await callback.message.answer(
        LEXICON[user.language]["user_deleted"],
        reply_markup=henchman_pass_keyboard(session, language),
    )


async def show_user_list(
    callback: CallbackQuery,
    state: FSMContext,
    session: Session,
    queryset: Callable,
    language: str,
    no_btn_cd: str,
    back_btn_cd: str,
    no_users_msg: str,
    msg: str,
    start_kbd: Any,
    **queryset_kwargs: dict,
):
    """Список пользователей для клавиатуры с множественным выбором.

    :param callback:
    :param state:
    :param session:
    :param queryset: Функция запроса к базе данных
    :param language: Язык сообщений
    :param no_btn_cd: Callback для кнопки 'Нет'
    :param back_btn_cd: Callback для кнопки 'Назад'
    :param no_users_msg: Сообщение при пустом запросе
    :param msg: Сообщение
    :param start_kbd: Клавиатура после удаления пользователя
    :param **queryset_kwargs: Параметры для запроса к базе данных
    """
    await state.clear()
    users = queryset(session, **queryset_kwargs)
    if not users:
        await callback.answer(no_users_msg)
    else:
        data = await data_for_multiselect_kb(users)
        await state.update_data(
            multiselect=data,
            no_btn_cd=no_btn_cd,
            back_btn_cd=back_btn_cd,
            language=language,
            start_kbd=start_kbd,
        )
        await callback.message.edit_text(
            text=msg,
            reply_markup=await multiselect_kb(data, language, back_btn_cd),
        )


@admin_router.callback_query(F.data == "show_admins")
@admin_router.callback_query(F.data == "no:delete_admin")
async def show_admins(
    callback: CallbackQuery, state: FSMContext, session: Session
):
    """Список администраторов."""
    try:
        await show_user_list(
            callback,
            state,
            session,
            get_users_by_role,
            "RU",
            "delete_admin",
            "superuser_keyboard",
            LEXICON["RU"]["no_admins"],
            LEXICON["RU"]["select_admins"],
            boss_pass_keyboard,
            **{"role": "master"},
        )
    except Exception as err:
        logger.error(f"Ошибка при поиске админов: {err}")


async def select_button(
    callback: CallbackQuery,
    state: FSMContext,
    is_selected: bool,
):
    """Обрабатывает нажатие кнопки."""
    await callback.answer()
    data = await state.get_data()
    user_id = re.search(r"^\d*", callback.data).group(0)
    data["multiselect"][int(user_id)]["selected"] = is_selected
    await callback.message.edit_reply_markup(
        reply_markup=await multiselect_kb(
            data["multiselect"], data["language"], data["back_btn_cd"]
        )
    )


@admin_router.callback_query(F.data.endswith("extend"))
async def select_users(
    callback: CallbackQuery, state: FSMContext, session: Session
):
    """Выбор пользователя."""
    try:
        await select_button(callback, state, True)
    except Exception as err:
        logger.error(f"Ошибка при выборе пользователя: {err}")


@admin_router.callback_query(F.data.endswith("collapse"))
async def unselect_users(
    callback: CallbackQuery, state: FSMContext, session: Session
):
    """Отмена выбора пользователя."""
    try:
        await select_button(callback, state, False)
    except Exception as err:
        logger.error(f"Ошибка при выборе пользователя: {err}")


@admin_router.callback_query(F.data == "delete_users")
async def delete_users(
    callback: CallbackQuery, state: FSMContext, session: Session
):
    """Показывает список выбранных пользователей для удаления."""
    try:
        data = await state.get_data()
        users_for_delete = []
        msg = [LEXICON[data["language"]]["delete_confirmation"]]
        for user_id, params in data["multiselect"].items():
            if params["selected"]:
                users_for_delete.append(user_id)
                msg.append(f"{params['name']} ({user_id})")
        if not users_for_delete:
            await callback.answer(LEXICON[data["language"]]["unselected"])
        else:
            await state.update_data(users_for_delete=users_for_delete)
            await callback.message.edit_text(
                text="\n".join(msg),
                reply_markup=yes_no_keyboard(
                    data["language"], "delete_users", data["no_btn_cd"]
                ),
            )

    except Exception as err:
        logger.error(f"Ошибка при удалении пользователя: {err}")


@admin_router.callback_query(F.data == "yes:delete_users")
async def delete_user_confirmation(
    callback: CallbackQuery, state: FSMContext, session: Session
):
    """Удаление пользователя."""
    try:
        await callback.answer()
        data = await state.get_data()
        await users_deleting(session, data["users_for_delete"])
        await state.clear()
        await callback.message.edit_text(
            text=LEXICON[data["language"]]["user_deleted"],
            reply_markup=data["start_kbd"](),
        )

    except Exception as err:
        logger.error(f"Ошибка при удалении пользователя: {err}")


@admin_router.callback_query(F.data == "superuser_keyboard")
async def superuser_lk(
    callback: CallbackQuery, state: FSMContext, session: Session
):
    """Кабинет супер пользователя."""
    try:
        await callback.answer()
        await state.clear()
        await callback.message.edit_text(
            text=LEXICON["RU"]["welcome_superuser"],
            reply_markup=boss_pass_keyboard(),
        )

    except Exception as err:
        logger.error(f"Ошибка при вызове клавиатуры суперпользователя: {err}")

import datetime
import hashlib
import logging
import os
import re
import shutil

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from aiogram.types.input_file import FSInputFile
from sqlalchemy.orm import Session

from config_data.config import load_config
from db.models import Password, Season
from keyboards.admin_keyboards import (
    boss_pass_keyboard,
    henchman_pass_keyboard,
    multiselect_kb,
)
from keyboards.keyboards import cancel_keyboard, yes_no_keyboard
from lexicon.lexicon import LEXICON
from utils.db_commands import get_users_by_role, users_deleting
from utils.states_form import (
    CounsellorPassword,
    KidPassword,
    MasterPassword,
    MethodistPassword,
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
async def change_kid_pass(callback: CallbackQuery, state: FSMContext):
    """Смена пароля ребенка."""
    await callback.message.delete()
    await callback.message.answer(
        text=LEXICON["RU"]["kid_pass"], reply_markup=cancel_keyboard()
    )
    await state.set_state(KidPassword.psw2hash)


# Обрабатываем пароль ребенка
@admin_router.message(StateFilter(KidPassword.psw2hash))
async def hashing_kid_password(
    message: Message, state: FSMContext, session: Session
):
    """Хешируем и сохраняем новый пароль ребенка."""
    psw_kid_hash = hashlib.sha256(message.text.encode())
    kid_psw = psw_kid_hash.hexdigest()
    session.query(Password).update({Password.kid_pass: kid_psw})
    await message.answer(text="Пароль обновлен")
    await state.clear()


@admin_router.callback_query(
    F.data == "counsellor_pass", StateFilter(default_state)
)
async def change_counsellor_pass(callback: CallbackQuery, state: FSMContext):
    """Смена пароля вожатого."""
    await callback.message.delete()
    await callback.message.answer(
        text=LEXICON["RU"]["counsellor_pass"], reply_markup=cancel_keyboard()
    )
    await state.set_state(CounsellorPassword.psw2hash)


# Обрабатываем пароль вожатого
@admin_router.message(StateFilter(CounsellorPassword.psw2hash))
async def hashing_counsellor_password(
    message: Message, state: FSMContext, session: Session
):
    """Хешируем и сохраняем новый пароль вожатого."""
    psw_counsellor_hash = hashlib.sha256(message.text.encode())
    counsellor_psw = psw_counsellor_hash.hexdigest()
    session.query(Password).update({Password.counsellor_pass: counsellor_psw})
    await message.answer(text="Пароль обновлен")
    await state.clear()


@admin_router.callback_query(
    F.data == "methodist_pass", StateFilter(default_state)
)
async def change_methodist_pass(callback: CallbackQuery, state: FSMContext):
    """Смена пароля методиста."""
    await callback.message.delete()
    await callback.message.answer(
        text=LEXICON["RU"]["methodist_pass"], reply_markup=cancel_keyboard()
    )
    await state.set_state(MethodistPassword.psw2hash)


# Обрабатываем пароль методиста
@admin_router.message(StateFilter(MethodistPassword.psw2hash))
async def hashing_methodist_password(
    message: Message, state: FSMContext, session: Session
):
    """Хешируем и сохраняем новый пароль методиста."""
    psw_methodist_hash = hashlib.sha256(message.text.encode())
    methodist_psw = psw_methodist_hash.hexdigest()
    session.query(Password).update({Password.methodist_pass: methodist_psw})
    await message.answer(text="Пароль обновлен")
    await state.clear()


@admin_router.callback_query(
    F.data == "master_pass", StateFilter(default_state)
)
async def change_master_pass(callback: CallbackQuery, state: FSMContext):
    """Смена мастер-пароля."""
    await callback.message.delete()
    await callback.message.answer(
        text=LEXICON["RU"]["master_pass"], reply_markup=cancel_keyboard()
    )
    await state.set_state(MasterPassword.psw2hash)


# Обрабатываем мастер-пароль
@admin_router.message(StateFilter(MasterPassword.psw2hash))
async def hashing_master_password(
    message: Message, state: FSMContext, session: Session
):
    """Хешируем и сохраняем новый мастер-пароль."""
    psw_master_hash = hashlib.sha256(message.text.encode())
    master_psw = psw_master_hash.hexdigest()
    session.query(Password).update({Password.master_pass: master_psw})
    await message.answer(text="Пароль обновлен")
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
        await callback.message.edit_reply_markup(
            reply_markup=henchman_pass_keyboard(session)
        )
    await state.clear()


@admin_router.callback_query(F.data == "open_season")
async def open_season(callback: CallbackQuery, session: Session):
    """Открываем сезон."""
    season = Season(
        open_season=datetime.datetime.now(),
    )
    session.add(season)
    session.commit()
    await callback.message.edit_reply_markup(
        text="Сезон открыт.", reply_markup=henchman_pass_keyboard(session)
    )


@admin_router.callback_query(F.data == "close_season")
async def close_season(callback: CallbackQuery, session: Session, bot):
    """Закрываем сезон."""
    season = session.query(Season).first()
    season.close_season = datetime.datetime.now()
    session.add(season)
    session.commit()
    try:
        await export_excel(callback, session, bot)
        delete_bd(session)
        await callback.message.answer(text="Сезон закрыт.")
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


@admin_router.callback_query(F.data == "show_admins")
@admin_router.callback_query(F.data == "no:delete_admin")
async def show_admins(
    query: CallbackQuery, state: FSMContext, session: Session
):
    """Список администраторов."""
    try:
        await state.clear()
        admins = get_users_by_role(session, "master")
        if not admins:
            await query.answer(LEXICON["RU"]["no_admins"])
        else:
            data = await data_for_multiselect_kb(admins)
            back_btn_cd = "superuser_keyboard"
            await state.update_data(
                multiselect=data,
                no_btn_cd="delete_admin",
                back_btn_cd=back_btn_cd,
            )
            await query.message.edit_text(
                text=LEXICON["RU"]["select_admins"],
                reply_markup=await multiselect_kb(data, back_btn_cd),
            )
    except Exception as err:
        logger.error(f"Ошибка при поиске админов: {err}")


@admin_router.callback_query(F.data.endswith("extend"))
async def select_users(
    callback: CallbackQuery, state: FSMContext, session: Session
):
    """Выбор пользователя."""
    try:
        await callback.answer()
        data = await state.get_data()
        user_id = re.search(r"^\d*", callback.data).group(0)
        data["multiselect"][int(user_id)]["selected"] = True
        await callback.message.edit_reply_markup(
            reply_markup=await multiselect_kb(
                data["multiselect"], data["back_btn_cd"]
            )
        )
    except Exception as err:
        logger.error(f"Ошибка при выборе пользователя: {err}")


@admin_router.callback_query(F.data.endswith("collapse"))
async def unselect_users(
    callback: CallbackQuery, state: FSMContext, session: Session
):
    """Отмена выбора пользователя."""
    try:
        await callback.answer()
        data = await state.get_data()
        user_id = re.search(r"^\d*", callback.data).group(0)
        data["multiselect"][int(user_id)]["selected"] = False
        await callback.message.edit_reply_markup(
            reply_markup=await multiselect_kb(
                data["multiselect"], data["back_btn_cd"]
            )
        )
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
        msg = [LEXICON["RU"]["delete_confirmation"]]
        for user_id, params in data["multiselect"].items():
            if params["selected"]:
                users_for_delete.append(user_id)
                msg.append(f"{params['name']} ({user_id})")
        if not users_for_delete:
            await callback.answer(LEXICON["RU"]["unselected"])
        else:
            await state.update_data(users_for_delete=users_for_delete)
            await callback.message.edit_text(
                text="\n".join(msg),
                reply_markup=yes_no_keyboard(
                    "RU", "delete_users", data["no_btn_cd"]
                ),
            )

    except Exception as err:
        logger.error(f"Ошибка при удалении пользователя: {err}")


@admin_router.callback_query(F.data == "yes:delete_users")
async def delete_user_confirmation(
    callback: CallbackQuery, state: FSMContext, session: Session
):
    """Удаление администратора."""
    try:
        await callback.answer()
        data = await state.get_data()
        await users_deleting(session, data["users_for_delete"])
        await state.clear()
        await callback.message.edit_text(
            text=LEXICON["RU"]["user_deleted"],
            reply_markup=boss_pass_keyboard(),
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

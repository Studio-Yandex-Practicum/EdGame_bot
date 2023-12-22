import datetime
import hashlib

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import Session

from config_data.config import load_config
from db.models import Password, Season, User
from keyboards.admin_keyboards import (
    boss_pass_keyboard,
    henchman_pass_keyboard,
    henchman_user_del_keyboard,
    user_del_keyboard,
)
from keyboards.keyboards import cancel_keyboard
from lexicon.lexicon import LEXICON
from utils.db_commands import select_user
from utils.states_form import (
    CounsellorPassword,
    KidPassword,
    MasterPassword,
    MethodistPassword,
    UserDel,
)

admin_router = Router()
config = load_config()


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
async def close_season(callback: CallbackQuery, session: Session):
    """Закрываем сезон."""
    season = session.query(Season).first()
    season.close_season = datetime.datetime.now()
    session.add(season)
    session.commit()
    # todo Здесь код экспорта в эксель
    # todo Удаление таблиц
    await callback.message.answer(text="Сезон закрыт.")


@admin_router.callback_query(F.data == "export_xls")
async def export_excel(callback: CallbackQuery, session: Session):
    """Экспорт в эксель."""
    # todo Экспорт в эксель
    pass


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
    await state.clear()
    await callback.message.edit_reply_markup(
        reply_markup=henchman_pass_keyboard(session)
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
    await callback.message.delete()
    user = select_user(session, callback.message.chat.id)
    user2del = session.query(User).filter_by(id=callback.data[:-4]).first()
    session.delete(user2del)
    await state.clear()
    await callback.message.answer(
        LEXICON[user.language]["user_deleted"],
        reply_markup=henchman_pass_keyboard(session),
    )

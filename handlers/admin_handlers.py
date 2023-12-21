import datetime
import hashlib

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import Session

from config_data.config import load_config
from db.models import Password, Season
from keyboards.admin_keyboards import (
    boss_pass_keyboard,
    henchman_pass_keyboard,
)
from keyboards.keyboards import cancel_keyboard
from lexicon.lexicon import LEXICON
from utils.db_commands import select_user
from utils.states_form import (
    CounsellorPassword,
    KidPassword,
    MasterPassword,
    MethodistPassword,
)

admin_router = Router()
config = load_config()


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
async def close_season(callback: CallbackQuery, session: Session):
    """Закрываем сезон."""
    user = select_user(session, callback.from_user.id)
    language = user.language
    season = session.query(Season).first()
    season.close_season = datetime.datetime.now()
    session.add(season)
    session.commit()
    # todo Здесь код экспорта в эксель
    # todo Удаление таблиц
    await callback.message.answer(text=LEXICON[language]["season_closed"])


@admin_router.callback_query(F.data == "export_xls")
async def export_excel(callback: CallbackQuery, session: Session):
    """Экспорт в эксель."""
    # todo Экспорт в эксель
    pass

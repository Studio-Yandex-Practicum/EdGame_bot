import datetime
import hashlib

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from config_data.config import load_config
from db.engine import engine, session
from db.models import Password, Season
from keyboards.admin_keyboards import (
    boss_pass_keyboard,
    henchman_pass_keyboard,
)
from keyboards.keyboards import cancel_keyboard
from lexicon.lexicon import LEXICON
from utils.states_form import (
    CounsellorPassword,
    KidPassword,
    MasterPassword,
    MethodistPassword,
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
async def hashing_kid_password(message: Message, state: FSMContext):
    """Хешируем и сохраняем новый пароль ребенка."""
    # Берем остальные пароли из базы
    conn = engine.connect()
    s = select(Password)
    r = conn.execute(s)
    row = r.fetchone()
    counsellor_psw = row[2]
    methodist_psw = row[3]
    master_psw = row[4]
    # Удаляем старые пароли в базе
    i = session.query(Password).first()
    session.delete(i)
    session.commit()
    # Обновляем пароль вожатого
    psw_kid_hash = hashlib.sha256(message.text.encode())
    kid_psw = psw_kid_hash.hexdigest()
    password = Password(
        kid_pass=kid_psw,
        master_pass=master_psw,
        counsellor_pass=counsellor_psw,
        methodist_pass=methodist_psw,
    )
    session.add(password)
    session.commit()
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
async def hashing_counsellor_password(message: Message, state: FSMContext):
    """Хешируем и сохраняем новый пароль вожатого."""
    # Берем остальные пароли из базы
    conn = engine.connect()
    s = select(Password)
    r = conn.execute(s)
    row = r.fetchone()
    kid_psw = row[1]
    methodist_psw = row[3]
    master_psw = row[4]
    # Удаляем старые пароли в базе
    i = session.query(Password).first()
    session.delete(i)
    session.commit()
    # Обновляем пароль вожатого
    psw_counsellor_hash = hashlib.sha256(message.text.encode())
    counsellor_psw = psw_counsellor_hash.hexdigest()
    password = Password(
        kid_pass=kid_psw,
        master_pass=master_psw,
        counsellor_pass=counsellor_psw,
        methodist_pass=methodist_psw,
    )
    session.add(password)
    session.commit()
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
async def hashing_methodist_password(message: Message, state: FSMContext):
    """Хешируем и сохраняем новый пароль методиста."""
    # Берем остальные пароли из базы
    conn = engine.connect()
    s = select(Password)
    r = conn.execute(s)
    row = r.fetchone()
    kid_psw = row[1]
    counsellor_psw = row[2]
    master_psw = row[4]
    # Удаляем старые пароли в базе
    i = session.query(Password).first()
    session.delete(i)
    session.commit()
    # Обновляем пароль методиста
    psw_methodist_hash = hashlib.sha256(message.text.encode())
    methodist_psw = psw_methodist_hash.hexdigest()
    password = Password(
        kid_pass=kid_psw,
        master_pass=master_psw,
        counsellor_pass=counsellor_psw,
        methodist_pass=methodist_psw,
    )
    session.add(password)
    session.commit()
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
async def hashing_master_password(message: Message, state: FSMContext):
    """Хешируем и сохраняем новый мастер-пароль."""
    # Берем остальные пароли из базы
    conn = engine.connect()
    s = select(Password)
    r = conn.execute(s)
    row = r.fetchone()
    kid_psw = row[1]
    counsellor_psw = row[2]
    methodist_psw = row[3]
    # Удаляем старые пароли в базе
    i = session.query(Password).first()
    session.delete(i)
    session.commit()
    # Обновляем мастер-пароль
    psw_master_hash = hashlib.sha256(message.text.encode())
    master_psw = psw_master_hash.hexdigest()
    password = Password(
        kid_pass=kid_psw,
        master_pass=master_psw,
        counsellor_pass=counsellor_psw,
        methodist_pass=methodist_psw,
    )
    session.add(password)
    session.commit()
    await message.answer(text="Пароль обновлен")
    await state.clear()


@admin_router.callback_query(F.data == "cancel")
async def cancel_pass(callback: CallbackQuery, state: FSMContext):
    """Отмена ввода пароля."""
    if callback.message.chat.id == config.boss_id:
        await callback.message.edit_reply_markup(
            reply_markup=boss_pass_keyboard()
        )
    else:
        await callback.message.edit_reply_markup(
            reply_markup=henchman_pass_keyboard()
        )
    await state.clear()


@admin_router.callback_query(F.data == "open_season")
async def open_season(callback: CallbackQuery):
    """Открываем сезон."""
    season = Season(
        open_season=datetime.datetime.now(),
    )
    session.add(season)
    session.commit()
    await callback.message.edit_reply_markup(
        text="Сезон открыт.", reply_markup=henchman_pass_keyboard()
    )


@admin_router.callback_query(F.data == "close_season")
async def close_season(callback: CallbackQuery):
    """Закрываем сезон."""
    season = session.query(Season).first()
    season.close_season = datetime.datetime.now()
    session.add(season)
    session.commit()
    # todo Здесь код экспорта в эксель
    # todo Удаление таблиц
    await callback.message.edit_reply_markup(
        text="Сезон закрыт.", reply_markup=henchman_pass_keyboard()
    )

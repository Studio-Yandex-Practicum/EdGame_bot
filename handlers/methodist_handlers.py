import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from filters.custom_filters import IsMethodist
from keyboards.keyboards import (
    create_welcome_keyboard,
    edit_profile_keyboard,
    help_keyboard,
)
from keyboards.methodist_keyboards import methodist_profile_keyboard
from lexicon.lexicon import BUTTONS, LEXICON
from utils.db_commands import select_user, set_user_param
from utils.states_form import Data
from utils.utils import generate_profile_info

from .methodist_task_handlers import methodist_task_router
from .methodist_team_handlers import methodist_team_router

logger = logging.getLogger(__name__)

methodist_router = Router()
methodist_router.include_routers(methodist_team_router, methodist_task_router)
methodist_router.message.filter(IsMethodist())
methodist_router.callback_query.filter(IsMethodist())


# Обработчики обычных кнопок
@methodist_router.message(F.text.in_([
    BUTTONS["RU"]["lk"],
    BUTTONS["TT"]["lk"],
    BUTTONS["EN"]["lk"]]))
async def profile_info(message: Message, state: FSMContext):
    '''Обработчик показывает главное меню профиля методиста.'''
    try:
        await state.clear()
        user = select_user(message.from_user.id)
        language = user.language
        lexicon = LEXICON[language]
        # Генерируем инфу для ЛК
        msg = generate_profile_info(user, lexicon)
        await message.answer(
            msg,
            reply_markup=methodist_profile_keyboard(language))
        await message.delete()
    except KeyError as err:
        logger.error(
            f'Ошибка в ключе при открытии личного кабинета методиста: {err}')
    except Exception as err:
        logger.error(f'Ошибка при открытии личного кабинета методиста: {err}')


@methodist_router.callback_query(F.data == 'profile')
async def profile_info_callback_query(query: CallbackQuery, state: FSMContext):
    '''Обработчик показывает главное меню профиля методиста.'''
    try:
        await query.answer()
        await state.clear()
        # Достаем инфу о пользователе из базы
        user = select_user(query.from_user.id)
        language = user.language
        lexicon = LEXICON[user.language]
        # Генерируем инфу для ЛК
        msg = generate_profile_info(user, lexicon)
        await query.message.answer(
            msg,
            reply_markup=methodist_profile_keyboard(language))
        await query.message.delete()
    except KeyError as err:
        logger.error(
            f'Ошибка в ключевом слове при открытии личного кабинета: {err}')
    except Exception as err:
        logger.error(f'Ошибка при открытии личного кабинета: {err}')


@methodist_router.message(F.text.in_([
    BUTTONS["RU"]["help"],
    BUTTONS["TT"]["help"],
    BUTTONS["EN"]["help"]]))
async def help_command(message: Message):
    try:
        user = select_user(message.from_user.id)
        language = user.language
        await message.answer(
            LEXICON[language]["help_info"],
            reply_markup=help_keyboard(language))
    except KeyError as err:
        logger.error(
            'Ошибка в ключевом слове при обработке команды help у методиста:'
            f' {err}')
    except Exception as err:
        logger.error(f'Ошибка при обработке команды help у методиста: {err}')


# Обработчики редактирования профиля
@methodist_router.message(F.text.in_([
    BUTTONS["RU"]["edit_profile"],
    BUTTONS["TT"]["edit_profile"],
    BUTTONS["EN"]["edit_profile"]]))
async def edit_profile(message: Message, state: FSMContext):
    '''Обработчик для редактирования профиля методиста.'''
    try:
        await state.clear()
        user = select_user(message.chat.id)
        await message.answer(
            LEXICON[user.language]["edit_profile"],
            reply_markup=edit_profile_keyboard(user.language))
    except KeyError as err:
        logger.error(f'Ошибка в ключевом слове при изменении профиля: {err}')
    except Exception as err:
        logger.error(f'Ошибка при изменении профиля: {err}')


@methodist_router.callback_query(F.data == 'change_name')
async def change_name(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик создает состояние для смены имени, просит
    прислать сообщение.
    '''
    try:
        await query.answer()
        await state.set_state(Data.change_name)
        user = select_user(query.from_user.id)
        await query.message.answer(
            LEXICON[user.language]["change_name"],
            reply_markup=ReplyKeyboardRemove())
        await query.message.delete()
    except KeyError as err:
        logger.error(f'Ошибка в ключевом слове при запросе имени: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе имени: {err}')


@methodist_router.message(Data.change_name)
async def process_change_name(message: Message, state: FSMContext):
    '''Обрабатывает сообщение для изменения имени.'''
    try:
        user = select_user(message.chat.id)
        set_user_param(user, name=message.text)
        await state.clear()
        await message.answer(
            LEXICON[user.language]["name_changed"],
            reply_markup=edit_profile_keyboard(user.language))
    except KeyError as err:
        logger.error(f'Ошибка в ключевом слове при изменении имени: {err}')
    except Exception as err:
        logger.error(f'Ошибка при изменении имени: {err}')


@methodist_router.callback_query(F.data == 'change_language')
async def change_language(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик создает состояние для смены языка, уточняет,
    какой язык установить.
    '''
    try:
        await query.answer()
        await state.set_state(Data.change_language)
        user = select_user(query.from_user.id)
        await query.message.edit_text(
            LEXICON[user.language]["change_language"],
            reply_markup=create_welcome_keyboard())
    except KeyError as err:
        logger.error(f'Ошибка в ключевом слове при запросе языка: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе языка: {err}')


@methodist_router.callback_query(Data.change_language)
async def process_change_language(query: CallbackQuery, state: FSMContext):
    '''Обработчик для изменения языка интерфейса.'''
    try:
        await query.answer()
        await state.clear()
        user = select_user(query.from_user.id)
        # Изменяем язык бота на новый
        language = query.data
        set_user_param(user, language=language)
        await query.message.edit_text(
            LEXICON[language]['language_changed'],
            reply_markup=edit_profile_keyboard(language))
    except KeyError as err:
        logger.error(f'Ошибка в ключевом слове при изменении языка: {err}')
    except Exception as err:
        logger.error(f'Ошибка при изменении языка: {err}')

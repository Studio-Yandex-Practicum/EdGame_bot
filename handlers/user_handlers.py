import logging

from typing import Dict, Any
from aiogram import Router, F, Bot
from aiogram.types import (
    Message, ReplyKeyboardMarkup, InlineKeyboardMarkup, CallbackQuery,
    ReplyKeyboardRemove)
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.keyboards import (
    menu_keyboard, profile_keyboard, edit_profile_keyboard, letsgo_keyboard,
    registered_keyboard, choose_language_keyboard, task_list_keyboard,
    task_keyboard)
from keyboards.methodist_keyboards import art_list_keyboard
from lexicon.lexicon import LEXICON_RU
from config.config import load_config
from .artefact_handlers import process_photo

logger = logging.getLogger(__name__)

router = Router()
child_router = Router()
router.include_router(child_router)

TASKS: dict = {
    'send_photo': {
        'status': 'open',
        'text': 'Пришли свое фото'
    },
    'send_video': {
        'status': 'open',
        'text': 'Пришли свое видео'
    },
    'write_article': {
        'status': 'in_review',
        'text': 'Напиши статью'
    }
}

ROLE = {'methodist': {}, 'councelor': {}, 'kid': {}}


class Data(StatesGroup):
    '''
    Машина состояний для реализации сценариев диалогов с пользователем.
    '''
    name = State()
    tasks = State()
    artefact = State()


# Этот хэндлер срабатывает на кодовое слово и присваивает роль методиста
@router.message(F.text.casefold() =='methodist')
async def process_methodist_command(message):
    # Проверяем не получал ли юзер ранее права вожатого
    if message.chat.id in ROLE['councelor']:
        await message.answer(text='У вас права доступа вожатого.')
    # Проверяем получал ли юзер права доступа ребенка, если да, то переносим id в права доступа методиста
    else:
        user_name = message.chat.first_name
        if message.chat.id in ROLE['kid']:
            user_name = ROLE['kid'][message.chat.id]
            del ROLE['kid'][message.chat.id]
        ROLE['methodist'][message.chat.id] = user_name
        await message.answer(text='Вы получили права доступа методиста.')


# Этот хэндлер срабатывает на кодовое слово и присваивает роль вожатого
@router.message(F.text.casefold() == 'councelor')
async def process_councelor_command(message):
    # Проверяем не получал ли юзер ранее права методиста
    if message.chat.id in ROLE['methodist']:
        await message.answer(text='У вас права доступа методиста.')
    # Проверяем получал ли юзер права доступа ребенка, если да, то переносим id в права доступа методиста
    else:
        user_name = message.chat.first_name
        if message.chat.id in ROLE['kid']:
            user_name = ROLE['kid'][message.chat.id]
            del ROLE['kid'][message.chat.id]
        ROLE['councelor'][message.chat.id] = user_name
        await message.answer(text='Вы получили права доступа вожатого.')


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    await state.set_state(Data.name)
    await message.answer(text=LEXICON_RU['/start'])


# Этот хэндлер получает и сохраняет имя пользователя
@child_router.message(Data.name)
async def process_name(message: Message, state: FSMContext):
    '''Обработчик после авторизации. (пока что команда старт)'''
    ROLE['kid'][message.chat.id] = message.text
    # Добавить код для внесения пользователя в базу
    print(ROLE['kid'])
    await state.clear()
    await message.answer(
        f'Привет, {message.text}! {LEXICON_RU["hello_message"]}',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=menu_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True)
    )


@child_router.message(F.text.regexp(r'^Посмотреть доступные ачивки$'))
async def show_tasks_list(message: Message, state: FSMContext):
    '''
    Обработчик кнопки Посмотреть доступные ачивки.
    Отправляет список открытых ачивок, сохраняет открытые
    ачивки и их id через Data.
    '''
    try:
        task_list = []
        task_state = {}
        count = 1
        await state.set_state(Data.tasks)
        for task in TASKS:
            if TASKS[task].get('status') == 'open':
                task_list.append(f'{count}: {TASKS[task].get("text")}.')
                task_state[count] = task
                count += 1
        text = '\n\n'.join(task_list)
        await state.update_data(tasks=task_state)
        await message.answer(
            f'{text}\n\nВыбери ачивку, которую хочешь выполнить:',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_list_keyboard)
        )
    except KeyError as err:
        logger.error(f'Проверь правильность ключевых слов: {err}')
    except Exception as err:
        logger.error(f'Ошибка при отправке списка ачивок. {err}')


@child_router.callback_query(F.data == 'show_tasks_list')
async def show_tasks_list_inline(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик инлайн кнопки Посмотреть доступные ачивки.
    Отправляет список открытых ачивок, сохраняет открытые
    ачивки и их id через Data.
    '''
    try:
        await query.answer()
        task_list = []
        task_state = {}
        count = 1
        await state.set_state(Data.tasks)
        for task in TASKS:
            if TASKS[task].get('status') == 'open':
                task_list.append(f'{count}: {TASKS[task].get("text")}.')
                task_state[count] = task
                count += 1
        text = '\n\n'.join(task_list)
        await state.update_data(tasks=task_state)
        await query.message.answer(
            f'{text}\n\nВыбери ачивку, которую хочешь выполнить:',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_list_keyboard)
        )
    except KeyError as err:
        logger.error(f'Проверь правильность ключевых слов: {err}')
    except Exception as err:
        logger.error(f'Ошибка при отправке списка ачивок. {err}')


@child_router.callback_query(Data.tasks)
@child_router.callback_query(F.data.in_(['1', '2', '3', '4']))
async def show_task(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик кнопок выбора отдельной ачивки.
    Получаем условный id ачивки из callback_data, достаем реальный id из
    состояние Data и получаем полную инфу об ачивке из базы данных.
    '''
    try:
        await query.answer()
        task_data = await state.get_data()
        if not task_data:
            await query.message.answer(
                'Вернись к списку ачивок и выбери заново(=',
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=task_keyboard)
            )
            return
        await state.set_state(Data.artefact)
        task_number = int(query.data)
        # Достаем id ачивки из состояния и делаем запрос к базе
        task_id = task_data['tasks'][task_number]
        task_info = TASKS[task_id].get('text')
        await query.message.answer(
            f'Итак, ты выбрал ачивку. Вот подробности:\n\n{task_info}\n\n'
            f'{LEXICON_RU["task_instruction"]}',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_keyboard)
        )
    except KeyError as err:
        logger.error(f'Проверь правильность ключевых слов: {err}')
    except Exception as err:
        logger.error(f'Ошибка при получении ачивки: {err}')


@child_router.message(Data.artefact)
async def process_artefact(message: Message, state: FSMContext):
    '''
    Обработчик артефактов, файлов, которые отправляет ребенок.
    '''
    try:
        config = load_config()
        bot = Bot(token=config.bot.token, parse_mode=ParseMode.HTML)
        methodist_id = message.from_user.id  # Достаем id профиля преподавателя в тг из базы
        await state.clear()
        if message.photo:
            await process_photo(message)
        elif message.video:
            pass
        elif message.document:
            pass
        elif message.voice:
            pass
        await bot.send_message(
            chat_id=methodist_id,
            text='Проверить артефакт',
            reply_markup=ReplyKeyboardMarkup(
                keyboard=art_list_keyboard,
                resize_keyboard=True,
                one_time_keyboard=True)
            )
        await message.answer(
            'Артефакт отправлен, ты молодец! Хочешь сделать еще одну ачивку?',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_keyboard)
        )
    except Exception as err:
        logger.error(f'Ошибка при обработке артефакта: {err}')


@child_router.message(F.text.regexp(r'^Личный кабинет$'))
async def profile_info(message: Message):
    '''Обработчик показывает главное меню профиля студента.'''
    # Достаем инфу о пользователе из базы
    info = LEXICON_RU['student_menu']
    await message.answer(
        info,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=profile_keyboard, resize_keyboard=True)
    )


@child_router.message(F.text.regexp(r'^Редактировать профиль$'))
async def edit_profile(message: Message):
    '''Обработчик для редактирования профиля ребенка.'''
    text = LEXICON_RU['edit_profile']
    await message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=edit_profile_keyboard)
    )


@child_router.callback_query(F.data == 'change_firstname')
async def edit_first_name(query: CallbackQuery):
    await query.answer()
    await query.message.answer(
        'Ок, пришли свое новое имя!',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=edit_profile_keyboard)
    )

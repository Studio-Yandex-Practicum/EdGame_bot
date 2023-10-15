import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Text, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from keyboards.keyboards import (
    menu_keyboard, profile_keyboard, edit_profile_keyboard,
    create_welcome_keyboard, contacts_keyboard, help_keyboard)
from keyboards.methodist_keyboards import methodist_profile_keyboard
from keyboards.counselor_keyboard import create_profile_keyboard
from lexicon.lexicon import LEXICON, LEXICON_COMMANDS, BUTTONS
from utils.db_commands import (
    register_user, select_user, is_user_in_db, set_user_param)
from utils.states_form import Data, Profile
from utils.utils import generate_profile_info
from db.engine import session
from filters.custom_filters import IsStudent
from middlewares.custom_middlewares import AcceptMediaGroupMiddleware
from .methodist_handlers import methodist_router
from .user_task_handlers import child_task_router
from .user_team_handlers import child_team_router

logger = logging.getLogger(__name__)

router = Router()
child_router = Router()
child_router.include_routers(child_task_router, child_team_router)
child_router.message.filter(IsStudent())
child_router.callback_query.filter(IsStudent())
child_router.message.middleware(AcceptMediaGroupMiddleware())
router.include_routers(methodist_router, child_router)


# Этот хэндлер срабатывает на кодовое слово и присваивает роль методиста
@router.message(Text(text="methodist"))
async def process_methodist_command(message: Message, state: FSMContext):
    await state.clear()
    user = select_user(message.chat.id)
    user.role = "methodist"
    session.add(user)
    session.commit()
    await message.answer(
        text=LEXICON[user.language]["methodist"],
        reply_markup=methodist_profile_keyboard(user.language)
    )


# Этот хэндлер срабатывает на кодовое слово и присваивает роль вожатого
@router.message(Text(text="councelor"))
async def process_councelor_command(message: Message, state: FSMContext):
    await state.clear()
    user = select_user(message.chat.id)
    user.role = "councelor"
    session.add(user)
    session.commit()
    if user.language == "ru":
        await message.answer(text=LEXICON["RU"]["councelor"])
    elif user.language == "tt":
        await message.answer(text=LEXICON["TT"]["councelor"])
    else:
        await message.answer(
            text=LEXICON[user.language]["councelor"],
            reply_markup=create_profile_keyboard())


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext):
    # Проверяем есть ли юзер в базе
    user = select_user(message.chat.id)
    if is_user_in_db(message.chat.id):
        await state.clear()
        await message.answer(f'Добро пожаловать, {user.name}',
                             reply_markup=menu_keyboard(user.language))
    else:
        # Анкетируем и сохраняем пользователя в БД, роль по умолчанию 'kid'
        await message.answer(
            text=f"{LEXICON_COMMANDS['/start']}",
            reply_markup=create_welcome_keyboard(),
        )
        await state.set_state(Profile.choose_language)


# Этот хендлер срабатывает на выбор языка
@router.callback_query(
    StateFilter(Profile.choose_language), F.data.in_(["RU", "TT", "EN"])
)
async def process_select_language(callback: CallbackQuery, state: FSMContext):
    await state.update_data(language=callback.data)
    if callback.data == "RU":
        text = LEXICON["RU"]["ru_pressed"]
    elif callback.data == "TT":
        text = LEXICON["TT"]["tt_pressed"]
    else:
        text = LEXICON["EN"]["en_pressed"]
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(Profile.get_name)


@router.message(StateFilter(Profile.get_name))
async def process_get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    user_language = await state.get_data()
    if user_language["language"] == "RU":
        text = LEXICON["RU"]["get_name"]
    elif user_language["language"] == "TT":
        text = LEXICON["TT"]["get_name"]
    else:
        text = LEXICON["EN"]["get_name"]
    await message.answer(text=text)
    await state.set_state(Profile.get_group)


@router.message(StateFilter(Profile.get_group))
async def process_get_group(message: Message, state: FSMContext):
    await state.update_data(group=message.text)
    await state.update_data(id=int(message.chat.id))
    user_data = await state.get_data()
    language = user_data["language"]
    if language == "RU":
        text = LEXICON["RU"]["get_group"]
    elif language == "TT":
        text = LEXICON["TT"]["get_group"]
    else:
        text = LEXICON["EN"]["get_group"]
    await message.answer(text=text, reply_markup=menu_keyboard(language))
    # Вносим данные пользователь в БД
    register_user(user_data)
    await state.clear()


# Меню ребенка
@child_router.message(
    F.text.in_([BUTTONS["RU"]["lk"], BUTTONS["TT"]["lk"], BUTTONS["EN"]["lk"]])
)
async def profile_info(message: Message, state: FSMContext):
    """Обработчик показывает главное меню профиля студента."""
    try:
        await state.clear()
        # Достаем инфу о пользователе из базы
        user = select_user(message.chat.id)
        lexicon = LEXICON[user.language]
        # Генерируем инфу для ЛК
        msg = generate_profile_info(user, lexicon)
        await message.answer(
            msg,
            reply_markup=profile_keyboard(user.language)
        )
        await message.delete()
    except KeyError as err:
        logger.error(
            f"Ошибка в ключевом слове при открытии личного кабинета: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при открытии личного кабинета: {err}")


@child_router.callback_query(F.data == "profile")
async def profile_info_callback_query(query: CallbackQuery, state: FSMContext):
    """Обработчик показывает главное меню профиля студента."""
    try:
        await query.answer()
        await state.clear()
        # Достаем инфу о пользователе из базы
        user = select_user(query.from_user.id)
        lexicon = LEXICON[user.language]
        # Генерируем инфу для ЛК
        msg = generate_profile_info(user, lexicon)
        await query.message.answer(
            msg,
            reply_markup=profile_keyboard(user.language)
        )
        await query.message.delete()
    except KeyError as err:
        logger.error(
            f"Ошибка в ключевом слове при открытии личного кабинета: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при открытии личного кабинета: {err}")


@child_router.message(
    F.text.in_(
        [BUTTONS["RU"]["write_to_councelor"],
         BUTTONS["TT"]["write_to_councelor"],
         BUTTONS["EN"]["write_to_councelor"]]))
async def write_to_councelor(message: Message):
    """
    Обработчик кнопки Написать вожатому.
    Отправляет инлайн кнопку со ссылкой на вожатого.
    """
    try:
        user = select_user(message.from_user.id)
        language = user.language
        # Как-то получаем username вожатого
        councelor = message.from_user.username
        await message.answer(
            LEXICON[language]["councelor_contact"],
            reply_markup=contacts_keyboard(language, councelor)
        )
    except KeyError as err:
        logger.error(
            f"Ошибка в ключевом слове при отправке контакта вожатого: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при отправке контакта вожатого: {err}")


@child_router.message(
    F.text.in_(
        [BUTTONS["RU"]["help"],
         BUTTONS["TT"]["help"],
         BUTTONS["EN"]["help"]]))
async def help_command(message: Message):
    try:
        user = select_user(message.from_user.id)
        language = user.language
        await message.answer(
            LEXICON[language]["help_info"],
            reply_markup=help_keyboard(language)
        )
    except KeyError as err:
        logger.error(
            f"Ошибка в ключевом слове при обработке команды help: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при обработке команды help: {err}")


# Обработчики редактирования профиля
@child_router.message(
    F.text.in_(
        [BUTTONS["RU"]["edit_profile"],
         BUTTONS["TT"]["edit_profile"],
         BUTTONS["EN"]["edit_profile"]]))
async def edit_profile(message: Message, state: FSMContext):
    """Обработчик для редактирования профиля ребенка."""
    try:
        await state.clear()
        user = select_user(message.chat.id)
        await message.answer(
            LEXICON[user.language]["edit_profile"],
            reply_markup=edit_profile_keyboard(user.language)
        )
    except KeyError as err:
        logger.error(f"Ошибка в ключевом слове при изменении профиля: {err}")
    except Exception as err:
        logger.error(f"Ошибка при изменении профиля: {err}")


@child_router.callback_query(F.data == "change_name")
async def change_name(query: CallbackQuery, state: FSMContext):
    """
    Обработчик создает состояние для смены имени, просит
    прислать сообщение.
    """
    try:
        await query.answer()
        await state.set_state(Data.change_name)
        user = select_user(query.from_user.id)
        await query.message.answer(
            LEXICON[user.language]["change_name"],
            reply_markup=ReplyKeyboardRemove(),
        )
        await query.message.delete()
    except KeyError as err:
        logger.error(f"Ошибка в ключевом слове при запросе имени: {err}")
    except Exception as err:
        logger.error(f"Ошибка при запросе имени: {err}")


@child_router.message(Data.change_name)
async def process_change_name(message: Message, state: FSMContext):
    """Обрабатывает сообщение для изменения имени."""
    try:
        user = select_user(message.chat.id)
        set_user_param(user, name=message.text)
        await state.clear()
        await message.answer(
            LEXICON[user.language]["name_changed"],
            reply_markup=edit_profile_keyboard(user.language)
        )
    except KeyError as err:
        logger.error(f"Ошибка в ключевом слове при изменении имени: {err}")
    except Exception as err:
        logger.error(f"Ошибка при изменении имени: {err}")


@child_router.callback_query(F.data == "change_language")
async def change_language(query: CallbackQuery, state: FSMContext):
    """
    Обработчик создает состояние для смены языка, уточняет,
    какой язык установить.
    """
    try:
        await query.answer()
        await state.set_state(Data.change_language)
        user = select_user(query.from_user.id)
        await query.message.edit_text(
            LEXICON[user.language]["change_language"],
            reply_markup=create_welcome_keyboard()
        )
    except KeyError as err:
        logger.error(f"Ошибка в ключевом слове при запросе языка: {err}")
    except Exception as err:
        logger.error(f"Ошибка при запросе языка: {err}")


@child_router.callback_query(Data.change_language)
async def process_change_language(query: CallbackQuery, state: FSMContext):
    """Обработчик для изменения языка интерфейса."""
    try:
        await query.answer()
        await state.clear()
        user = select_user(query.from_user.id)
        # Изменяем язык бота на новый
        language = query.data
        set_user_param(user, language=language)
        await query.message.edit_text(
            LEXICON[language]["language_changed"],
            reply_markup=edit_profile_keyboard(language)
        )
    except KeyError as err:
        logger.error(f"Ошибка в ключевом слове при изменении языка: {err}")
    except Exception as err:
        logger.error(f"Ошибка при изменении языка: {err}")

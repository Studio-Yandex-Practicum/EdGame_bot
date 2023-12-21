import hashlib
import logging

from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from sqlalchemy import select
from sqlalchemy.orm import Session

from config_data.config import load_config
from db.engine import engine
from db.models import Password
from filters.custom_filters import IsStudent
from keyboards.admin_keyboards import (
    boss_pass_keyboard,
    henchman_pass_keyboard,
)
from keyboards.counsellor_keyboard import create_profile_keyboard
from keyboards.keyboards import (
    contacts_keyboard,
    create_welcome_keyboard,
    edit_profile_keyboard,
    help_keyboard,
    menu_keyboard,
    profile_keyboard,
)
from keyboards.methodist_keyboards import methodist_profile_keyboard
from lexicon.lexicon import BUTTONS, LEXICON, LEXICON_COMMANDS
from middlewares.custom_middlewares import AcceptMediaGroupMiddleware
from utils.db_commands import (
    check_password,
    is_user_in_db,
    register_user,
    select_user,
    set_user_param,
)
from utils.states_form import Data, EnteringPassword, Profile
from utils.utils import generate_profile_info

from .admin_handlers import admin_router
from .methodist_handlers import methodist_router
from .user_task_handlers import child_task_router
from .user_team_handlers import child_team_router

logger = logging.getLogger(__name__)
config = load_config()

router = Router()
child_router = Router()
child_router.include_routers(child_task_router, child_team_router)
child_router.message.filter(IsStudent())
child_router.callback_query.filter(IsStudent())
child_router.message.middleware(AcceptMediaGroupMiddleware())
router.include_routers(methodist_router, child_router, admin_router)


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(
    message: Message, state: FSMContext, session: Session
):
    # Проверяем установлены ли пароли на роли
    check_password(session)

    # Проверяем есть ли юзер в базе и если нет, то регистрируем
    if message.chat.id == config.boss_id:
        await state.clear()
        await message.answer(
            lexicon["welcome_boss"], reply_markup=boss_pass_keyboard()
        )
    elif is_user_in_db(session, message.chat.id):
        user = select_user(session, message.chat.id)
        language = user.language
        lexicon = LEXICON[language]
        await state.clear()
        if user.role == "kid":
            await message.answer(
                f"{lexicon['welcome']}, {user.name}",
                reply_markup=menu_keyboard(language),
            )
        elif user.role == "counsellor":
            await message.answer(
                f"{lexicon['welcome']}, {user.name}",
                reply_markup=create_profile_keyboard(language),
            )
        elif user.role == "methodist":
            await message.answer(
                f"{lexicon['welcome']}, {user.name}",
                reply_markup=methodist_profile_keyboard(language),
            )
        else:
            await message.answer(
                f"{lexicon['welcome']}, {user.name}",
                reply_markup=henchman_pass_keyboard(session, language),
            )
    else:
        # Анкетируем и сохраняем пользователя в БД
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
    text = LEXICON[callback.data]["language_selected"]
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(Profile.get_name)


@router.message(StateFilter(Profile.get_name), F.text.isalpha())
async def process_get_name(message: Message, state: FSMContext):
    """Ввод имени."""
    await state.update_data(name=message.text)
    user_data = await state.get_data()
    language = user_data["language"]
    text = LEXICON[language]["get_name"]
    await message.answer(text=text)
    await state.set_state(Profile.get_group)


@router.message(StateFilter(Profile.get_name))
async def warning_not_name(message: Message, state: FSMContext):
    """Проверка, что пользователь ввел буквы в имени."""
    user_data = await state.get_data()
    language = user_data["language"]
    text = LEXICON[language]["err_name"]
    await message.answer(text)


@router.message(StateFilter(Profile.get_group), F.text.isdigit())
async def process_get_group(
    message: Message, state: FSMContext, session: Session
):
    """Приглашаем ввести пароль."""
    await state.update_data(group=message.text)
    await state.update_data(id=int(message.chat.id))
    user_data = await state.get_data()
    language = user_data["language"]
    text = LEXICON[language]["get_group"]
    await message.answer(text=text)
    # Вносим данные пользователь в БД
    register_user(session, user_data)
    await state.set_state(EnteringPassword.psw2hash)


@router.message(StateFilter(Profile.get_group))
async def warning_not_group(message: Message, state: FSMContext):
    """Проверка, что пользователь ввел цифры в группе."""
    user_data = await state.get_data()
    language = user_data["language"]
    text = LEXICON[language]["err_group"]
    await message.answer(text)


@admin_router.message(StateFilter(EnteringPassword.psw2hash))
async def hashing_password(
    message: Message, state: FSMContext, session: Session
):
    """Обрабатываем пароль."""
    user = select_user(session, message.chat.id)
    # переводим введенный юзером пароль в хеш
    psw_hash = hashlib.sha256(message.text.encode())
    psw = psw_hash.hexdigest()
    # сравниваем с паролем из базы
    conn = engine.connect()
    s = select(Password)
    r = conn.execute(s)
    row = r.fetchone()
    kid_psw = row[1]
    counsellor_psw = row[2]
    methodist_psw = row[3]
    master_psw = row[4]
    if psw == kid_psw:
        user.role = "kid"
        session.add(user)
        session.commit()
        await message.answer(
            text=LEXICON[user.language]["kid"],
            reply_markup=menu_keyboard(user.language),
        )
        await state.clear()
    elif psw == counsellor_psw:
        user.role = "counsellor"
        session.add(user)
        session.commit()
        await message.answer(
            text=LEXICON[user.language]["counsellor"],
            reply_markup=create_profile_keyboard(user.language),
        )
        await state.clear()
    elif psw == methodist_psw:
        user.role = "methodist"
        session.add(user)
        session.commit()
        await message.answer(
            text=LEXICON[user.language]["methodist"],
            reply_markup=methodist_profile_keyboard(user.language),
        )
        await state.clear()
    elif psw == master_psw:
        user.role = "master"
        session.add(user)
        session.commit()
        await message.answer(
            text=LEXICON[user.language]["master"],
            reply_markup=henchman_pass_keyboard(session, user.language),
        )
        await state.clear()
    else:
        await message.answer(text=LEXICON[user.language]["wrong_pass"])


# Меню ребенка
@child_router.message(
    F.text.in_([BUTTONS["RU"]["lk"], BUTTONS["TT"]["lk"], BUTTONS["EN"]["lk"]])
)
async def profile_info(message: Message, state: FSMContext, session: Session):
    """Обработчик показывает главное меню профиля студента."""
    try:
        await state.clear()
        # Достаем инфу о пользователе из базы
        user = select_user(session, message.chat.id)
        lexicon = LEXICON[user.language]
        # Генерируем инфу для ЛК
        msg = generate_profile_info(user, lexicon)
        await message.answer(msg, reply_markup=profile_keyboard(user.language))
        await message.delete()
    except KeyError as err:
        logger.error(
            f"Ошибка в ключевом слове при открытии личного кабинета: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при открытии личного кабинета: {err}")


@child_router.callback_query(F.data == "profile")
async def profile_info_callback_query(
    query: CallbackQuery, state: FSMContext, session: Session
):
    """Обработчик показывает главное меню профиля студента."""
    try:
        await query.answer()
        await state.clear()
        # Достаем инфу о пользователе из базы
        user = select_user(session, query.from_user.id)
        lexicon = LEXICON[user.language]
        # Генерируем инфу для ЛК
        msg = generate_profile_info(user, lexicon)
        await query.message.answer(
            msg, reply_markup=profile_keyboard(user.language)
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
        [
            BUTTONS["RU"]["write_to_counsellor"],
            BUTTONS["TT"]["write_to_counsellor"],
            BUTTONS["EN"]["write_to_counsellor"],
        ]
    )
)
async def write_to_counsellor(message: Message, session: Session):
    """Обработчик кнопки 'Написать вожатому'.

    Отправляет инлайн кнопку со ссылкой на вожатого.
    """
    try:
        user = select_user(session, message.from_user.id)
        language = user.language
        # Как-то получаем username вожатого
        counsellor = message.from_user.username
        await message.answer(
            LEXICON[language]["counsellor_contact"],
            reply_markup=contacts_keyboard(language, counsellor),
        )
    except KeyError as err:
        logger.error(
            f"Ошибка в ключевом слове при отправке контакта вожатого: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при отправке контакта вожатого: {err}")


@child_router.message(
    F.text.in_(
        [BUTTONS["RU"]["help"], BUTTONS["TT"]["help"], BUTTONS["EN"]["help"]]
    )
)
async def help_command(message: Message, session: Session):
    try:
        user = select_user(session, message.from_user.id)
        language = user.language
        await message.answer(
            LEXICON[language]["help_info"],
            reply_markup=help_keyboard(language),
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
        [
            BUTTONS["RU"]["edit_profile"],
            BUTTONS["TT"]["edit_profile"],
            BUTTONS["EN"]["edit_profile"],
        ]
    )
)
async def edit_profile(message: Message, state: FSMContext, session: Session):
    """Обработчик для редактирования профиля ребенка."""
    try:
        await state.clear()
        user = select_user(session, message.chat.id)
        await message.answer(
            LEXICON[user.language]["edit_profile"],
            reply_markup=edit_profile_keyboard(user.language),
        )
    except KeyError as err:
        logger.error(f"Ошибка в ключевом слове при изменении профиля: {err}")
    except Exception as err:
        logger.error(f"Ошибка при изменении профиля: {err}")


@child_router.callback_query(F.data == "change_name")
async def change_name(
    query: CallbackQuery, state: FSMContext, session: Session
):
    """Обработчик создает состояние для смены имени.

    Просит прислать сообщение.
    """
    try:
        await query.answer()
        await state.set_state(Data.change_name)
        user = select_user(session, query.from_user.id)
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
async def process_change_name(
    message: Message, state: FSMContext, session: Session
):
    """Обрабатывает сообщение для изменения имени."""
    try:
        user = select_user(session, message.chat.id)
        set_user_param(session, user, name=message.text)
        await state.clear()
        await message.answer(
            LEXICON[user.language]["name_changed"],
            reply_markup=edit_profile_keyboard(user.language),
        )
    except KeyError as err:
        logger.error(f"Ошибка в ключевом слове при изменении имени: {err}")
    except Exception as err:
        logger.error(f"Ошибка при изменении имени: {err}")


@child_router.callback_query(F.data == "change_language")
async def change_language(
    query: CallbackQuery, state: FSMContext, session: Session
):
    """Обработчик создает состояние для смены языка.

    Уточняет, какой язык установить.
    """
    try:
        await query.answer()
        await state.set_state(Data.change_language)
        user = select_user(session, query.from_user.id)
        await query.message.edit_text(
            LEXICON[user.language]["change_language"],
            reply_markup=create_welcome_keyboard(),
        )
    except KeyError as err:
        logger.error(f"Ошибка в ключевом слове при запросе языка: {err}")
    except Exception as err:
        logger.error(f"Ошибка при запросе языка: {err}")


@child_router.callback_query(Data.change_language)
async def process_change_language(
    query: CallbackQuery, state: FSMContext, session: Session
):
    """Обработчик для изменения языка интерфейса."""
    try:
        await query.answer()
        await state.clear()
        user = select_user(session, query.from_user.id)
        # Изменяем язык бота на новый
        language = query.data
        set_user_param(session, user, language=language)
        await query.message.edit_text(
            LEXICON[language]["language_changed"],
            reply_markup=edit_profile_keyboard(language),
        )
    except KeyError as err:
        logger.error(f"Ошибка в ключевом слове при изменении языка: {err}")
    except Exception as err:
        logger.error(f"Ошибка при изменении языка: {err}")

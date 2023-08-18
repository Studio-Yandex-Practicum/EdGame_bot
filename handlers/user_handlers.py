import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardMarkup, Message,
                           ReplyKeyboardMarkup, ReplyKeyboardRemove)

from data.temp_db import ROLE, TASKS
from db.engine import session
from keyboards.keyboards import (choose_language_keyboard,
                                 create_welcome_keyboard,
                                 edit_profile_keyboard, menu_keyboard,
                                 profile_keyboard, task_keyboard,
                                 task_list_keyboard)
from keyboards.methodist_keyboards import art_list_keyboard
from lexicon.lexicon import LEXICON, LEXICON_COMMANDS
from utils.db_commands import register_user, select_user

from .artifact_handlers import (process_audio, process_document, process_photo,
                                process_video, process_voice)

logger = logging.getLogger(__name__)


router = Router()
child_router = Router()
router.include_router(child_router)


class Data(StatesGroup):
    """
    Машина состояний для реализации сценариев диалогов с пользователем.
    """

    name = State()
    change_name = State()
    change_bio = State()
    change_language = State()
    tasks = State()
    artefact = State()


# Этот хэндлер срабатывает на кодовое слово и присваивает роль методиста
@router.message(Text(text="methodist"))
async def process_methodist_command(message):
    user = select_user(message.chat.id)
    user.role = "methodist"
    session.add(user)
    session.commit()
    if user.language == "ru":
        await message.answer(text=LEXICON["RU"]["methodist"])
    elif user.language == "tt":
        await message.answer(text=LEXICON["TT"]["methodist"])
    else:
        await message.answer(text=LEXICON["EN"]["methodist"])


# Этот хэндлер срабатывает на кодовое слово и присваивает роль вожатого
@router.message(Text(text="councelor"))
async def process_councelor_command(message):
    user = select_user(message.chat.id)
    user.role = "councelor"
    session.add(user)
    session.commit()
    if user.language == "ru":
        await message.answer(text=LEXICON["RU"]["councelor"])
    elif user.language == "tt":
        await message.answer(text=LEXICON["TT"]["councelor"])
    else:
        await message.answer(text=LEXICON["EN"]["councelor"])


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message):
    # Сохраняем пользователя в БД, роль по умолчанию 'kid'
    register_user(message)
    await message.answer(
        text=f"{LEXICON_COMMANDS['/start']}", reply_markup=create_welcome_keyboard()
    )


# Этот хендлер срабатывает на апдейт CallbackQuery с выбором языка
@router.callback_query(Text(text=["ru_pressed", "tt_pressed", "en_pressed"]))
async def process_buttons_press(callback):
    user = select_user(callback.from_user.id)
    if callback.data == "ru_pressed":
        user.language = "ru"
        session.add(user)
        session.commit()
        text = LEXICON["RU"]["ru_pressed"]
    elif callback.data == "tt_pressed":
        user.language = "tt"
        session.add(user)
        session.commit()
        text = LEXICON["TT"]["tt_pressed"]
    else:
        user.language = "en"
        session.add(user)
        session.commit()
        text = LEXICON["EN"]["en_pressed"]
    await callback.answer(text=text)


# Этот хэндлер получает и сохраняет имя пользователя
@child_router.message(Data.name)
async def process_name(message: Message, state: FSMContext):
    """Обработчик после авторизации."""
    ROLE["kid"][message.chat.id] = message.text
    # Добавить код для внесения пользователя в базу
    await state.clear()
    await message.answer(
        f'Привет, {message.text}! {LEXICON["RU"]["hello_message"]}',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=menu_keyboard, resize_keyboard=True, one_time_keyboard=True
        ),
    )


@child_router.message(F.text.regexp(r"^Посмотреть доступные ачивки$"))
@child_router.message(Command(commands="achievements"))
async def show_tasks_list(message: Message, state: FSMContext):
    """
    Обработчик кнопки Посмотреть доступные ачивки.
    Отправляет список открытых ачивок, сохраняет открытые
    ачивки и их id через Data.
    """
    try:
        task_list = []
        task_state = {}
        count = 0
        await state.set_state(Data.tasks)
        for task in TASKS:
            if TASKS[task].get("status") == "open":
                count += 1
                task_list.append(f'{count}: {TASKS[task].get("text")}.')
                task_state[count] = task
        text = "\n\n".join(task_list)
        await state.update_data(tasks=task_state)
        await message.answer(
            "Вот доступные тебе ачивки:\n\n"
            f"{text}\n\nВыбери ачивку, которую хочешь выполнить:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_list_keyboard[count]
            ),
        )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при отправке списка ачивок. {err}")


@child_router.callback_query(F.data == "show_tasks_list")
async def show_tasks_list_inline(query: CallbackQuery, state: FSMContext):
    """
    Обработчик инлайн кнопки Посмотреть доступные ачивки.
    Отправляет список открытых ачивок, сохраняет открытые
    ачивки и их id через Data.
    """
    try:
        await query.answer()
        task_list = []
        task_state = {}
        count = 0
        await state.set_state(Data.tasks)
        for task in TASKS:
            if TASKS[task].get("status") == "open":
                count += 1
                task_list.append(f'{count}: {TASKS[task].get("text")}.')
                task_state[count] = task
        text = "\n\n".join(task_list)
        await state.update_data(tasks=task_state)
        await query.message.answer(
            "Вот доступные тебе ачивки:\n\n"
            f"{text}\n\nВыбери ачивку, которую хочешь выполнить:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_list_keyboard[count]
            ),
        )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при отправке списка ачивок. {err}")


@child_router.callback_query(Data.tasks)
@child_router.callback_query(F.data.in_(["1", "2", "3", "4"]))
async def show_task(query: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопок выбора отдельной ачивки.
    Получаем условный id ачивки из callback_data, достаем реальный id из
    состояние Data и получаем полную инфу об ачивке из базы данных.
    """
    try:
        await query.answer()
        task_data = await state.get_data()
        if not task_data:
            await query.message.answer(
                "Вернись к списку ачивок и выбери заново(=",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=task_keyboard),
            )
            return
        await state.set_state(Data.artefact)
        task_number = int(query.data)
        # Достаем id ачивки из состояния и делаем запрос к базе
        task_id = task_data["tasks"][task_number]
        task_info = TASKS[task_id].get("text")
        await query.message.answer(
            f"Итак, ты выбрал ачивку. Вот подробности:\n\n{task_info}\n\n"
            f'{LEXICON["RU"]["task_instruction"]}',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=task_keyboard),
        )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при получении ачивки: {err}")


@child_router.message(Data.artefact)
async def process_artefact(message: Message, state: FSMContext, bot: Bot):
    """
    Обработчик артефактов, файлов, которые отправляет ребенок.
    """
    try:
        # Достаем id профиля преподавателя в тг из базы
        methodist_id = ROLE["methodist"].get("id")
        await state.clear()
        if message.photo:
            await process_photo(message)
        elif message.video:
            await process_video(message)
        elif message.document:
            await process_document(message)
        elif message.voice:
            await process_voice(message)
        elif message.audio:
            await process_audio(message)
        await bot.send_message(
            chat_id=methodist_id,
            text="Проверить артефакт",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=art_list_keyboard, resize_keyboard=True, one_time_keyboard=True
            ),
        )
        await message.answer(
            "Артефакт отправлен, ты молодец! Хочешь сделать еще одну ачивку?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=task_keyboard),
        )
    except Exception as err:
        logger.error(f"Ошибка при обработке артефакта: {err}")


@child_router.message(Command(commands="current_achievements"))
async def show_current_tasks(message: Message):
    """
    Показывам ачивки в статусе на проверке либо предлагаем
    перейти к списку ачивок.
    """
    try:
        # Достаем из базы ачивки со статусом на проверке
        in_review = []
        count = 0
        for task in TASKS:
            # Добавляем описания ачивок в список
            if TASKS[task].get("status") == "in_review":
                count += 1
                task_info = (
                    f'{count}: {TASKS[task].get("status")}\n'
                    f'{TASKS[task].get("text")}'
                )
                in_review.append(task_info)
            if TASKS[task].get("status") == "approved":
                count += 1
                task_info = (
                    f'{count}: {TASKS[task].get("status")}\n'
                    f'{TASKS[task].get("text")}'
                )
                in_review.append(task_info)
        if not in_review:
            await message.answer(
                "Кажется, ты еще не выполнил ни одной ачивки...\n\n" "Готов начать?=)",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=task_keyboard),
            )
        text = "\n\n".join(in_review)
        await message.answer(
            f"Ты молодец, делаешь много ачивок. Вот что ты уже сделал:\n\n"
            f"{text}\n\nПродолжай в том же духе!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=task_keyboard),
        )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при получении текущих ачивок: {err}")


@child_router.message(F.text.regexp(r"^Личный кабинет$"))
@child_router.message(Command(commands="lk"))
async def profile_info(message: Message):
    """Обработчик показывает главное меню профиля студента."""
    # Достаем инфу о пользователе из базы
    name = message.from_user.first_name  # достать из базы
    score = 12  # Достать из базы
    group_number = 21  # Достать из базы
    info = (
        f'{LEXICON["RU"]["student_profile"]}\n\n'
        f"Информация:\nИмя - {name}\nБаллы - {score}\n"
        f"Номер группы - {group_number}\nЦель - Перегнать всех."
    )
    await message.answer(
        info,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=profile_keyboard, resize_keyboard=True, one_time_keyboard=True
        ),
    )


@child_router.message(F.text.regexp(r"^Редактировать профиль$"))
async def edit_profile(message: Message):
    """Обработчик для редактирования профиля ребенка."""
    text = LEXICON["RU"]["edit_profile"]
    await message.answer(
        text, reply_markup=InlineKeyboardMarkup(inline_keyboard=edit_profile_keyboard)
    )


@child_router.callback_query(F.data == "change_name")
async def change_name(query: CallbackQuery, state: FSMContext):
    """
    Обработчик создает состояние для смены имени, просит
    прислать сообщение.
    """
    await query.answer()
    await state.set_state(Data.change_name)
    await query.message.answer(
        "Ок, пришли свое новое имя!", reply_markup=ReplyKeyboardRemove()
    )


@child_router.message(Data.change_name)
async def process_change_name(message: Message, state: FSMContext):
    """Обрабатывает сообщение для изменения имени."""
    # обновляем инфу о пользователе в базе данных
    await message.answer(
        f"Ок, {message.text}, теперь у тебя новое имя!\n\n" "Еще что-то надо изменить?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=edit_profile_keyboard),
    )


@child_router.callback_query(F.data == "change_language")
async def change_language(query: CallbackQuery, state: FSMContext):
    """
    Обработчик создает состояние для смены языка, уточняет,
    какой язык установить.
    """
    await query.answer()
    await state.set_state(Data.change_language)
    await state.update_data(
        change_language={"russian": "RU", "english": "EN", "tatar": "TATAR"}
    )
    await query.message.edit_text(
        "Ок, какой язык предпочитаешь?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=choose_language_keyboard),
    )


@child_router.callback_query(Data.change_language)
async def process_change_language(query: CallbackQuery, state: FSMContext):
    """Обработчик для изменения языка интерфейса."""
    await query.answer()
    data = await state.get_data()
    if not data:
        await query.message.answer(
            "Выбери раздел для изменения.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=edit_profile_keyboard),
        )
        return
    await state.clear()
    language = data["change_language"].get(query.data)
    # Изменяем язык бота на новый
    await query.message.answer(
        LEXICON[language]["language_changed"],
        reply_markup=InlineKeyboardMarkup(inline_keyboard=edit_profile_keyboard),
    )

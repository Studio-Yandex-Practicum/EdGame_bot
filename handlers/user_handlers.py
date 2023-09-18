import logging

from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    CallbackQuery,
    ReplyKeyboardRemove,
)
from aiogram.filters import CommandStart, Text, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from keyboards.keyboards import (
    menu_keyboard,
    profile_keyboard,
    edit_profile_keyboard,
    # choose_language_keyboard,
    task_list_keyboard,
    task_keyboard,
    create_welcome_keyboard,
    contacts_keyboard,
    help_keyboard,
)
from keyboards.methodist_keyboards import (
    art_list_keyboard,
    methodist_profile_keyboard,
)
from keyboards.counselor_keyboard import create_profile_keyboard
from lexicon.lexicon import LEXICON, LEXICON_COMMANDS, BUTTONS
from utils.db_commands import (
    register_user,
    select_user,
    set_user_param,
    available_achievements,
    get_users_by_role,
)
from utils.states_form import Data, Profile
from utils.utils import (
    process_next_achievements,
    process_previous_achievements,
    process_artifact,
    generate_text_with_tasks_in_review,
    generate_text_with_reviewed_tasks,
    generate_profile_info,
    get_achievement_info,
    process_artifact_group,
)
from db.engine import session
from config_data.config import Pagination
from filters.custom_filters import IsStudent
from middlewares.custom_middlewares import AcceptMediaGroupMiddleware
from .methodist_handlers import methodist_router

logger = logging.getLogger(__name__)

router = Router()
child_router = Router()
child_router.message.filter(IsStudent())
child_router.callback_query.filter(IsStudent())
child_router.message.middleware(AcceptMediaGroupMiddleware())
router.include_routers(methodist_router, child_router)


# Этот хэндлер срабатывает на кодовое слово и присваивает роль методиста
@router.message(Text(text="methodist"))
async def process_methodist_command(message: Message):
    user = select_user(message.chat.id)
    user.role = "methodist"
    session.add(user)
    session.commit()
    await message.answer(
        text=LEXICON[user.language]["methodist"],
        reply_markup=ReplyKeyboardMarkup(
            keyboard=methodist_profile_keyboard(user.language),
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )


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
        await message.answer(
            text=LEXICON[user.language]["councelor"],
            reply_markup=create_profile_keyboard())


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext):
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


# Обработчики обычных кнопок
@child_router.message(
    F.text.in_(
        [
            BUTTONS["RU"]["current_achievements"],
            BUTTONS["TT"]["current_achievements"],
            BUTTONS["EN"]["current_achievements"],
        ]
    )
)
async def show_current_tasks(message: Message):
    """
    Показывам ачивки в статусе на проверке либо предлагаем
    перейти к списку ачивок.
    """
    try:
        # Достаем из базы ачивки со статусом на проверке
        user = select_user(message.from_user.id)
        lexicon = LEXICON[user.language]
        # Генерируем текст с инфой об ачивках
        msg = generate_text_with_tasks_in_review(user.id, lexicon)
        await message.answer(
            msg,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_keyboard(user.language)
            ),
        )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при получении текущих ачивок: {err}")


@child_router.message(
    F.text.in_(
        [
            BUTTONS["RU"]["reviewed_achievements"],
            BUTTONS["TT"]["reviewed_achievements"],
            BUTTONS["EN"]["reviewed_achievements"],
        ]
    )
)
async def show_reviewed_tasks(message: Message):
    """
    Показывам ачивки в статусе на проверке либо предлагаем
    перейти к списку ачивок.
    """
    try:
        # Достаем из базы ачивки со статусом на проверке
        user = select_user(message.from_user.id)
        lexicon = LEXICON[user.language]
        # Генерируем текст с инфой об ачивках
        msg = generate_text_with_reviewed_tasks(user.id, lexicon)
        await message.answer(
            msg,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_keyboard(user.language)
            ),
        )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при получении проверенных ачивок: {err}")


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
            reply_markup=ReplyKeyboardMarkup(
                keyboard=profile_keyboard(user.language),
                resize_keyboard=True,
                one_time_keyboard=True,
            ),
        )
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
            reply_markup=ReplyKeyboardMarkup(
                keyboard=profile_keyboard(user.language),
                resize_keyboard=True,
                one_time_keyboard=True,
            ),
        )
    except KeyError as err:
        logger.error(
            f"Ошибка в ключевом слове при открытии личного кабинета: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при открытии личного кабинета: {err}")


@child_router.message(
    F.text.in_(
        [
            BUTTONS["RU"]["write_to_councelor"],
            BUTTONS["TT"]["write_to_councelor"],
            BUTTONS["EN"]["write_to_councelor"],
        ]
    )
)
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
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=contacts_keyboard(language, councelor)
            ),
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
async def help_command(message: Message):
    try:
        user = select_user(message.from_user.id)
        language = user.language
        await message.answer(
            LEXICON[language]["help_info"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=help_keyboard(language)
            ),
        )
    except KeyError as err:
        logger.error(
            f"Ошибка в ключевом слове при обработке команды help: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при обработке команды help: {err}")


# Обработчики списка ачивок и пагинации
@child_router.message(
    F.text.in_(
        [
            BUTTONS["RU"]["available_achievements"],
            BUTTONS["TT"]["available_achievements"],
            BUTTONS["EN"]["available_achievements"],
        ]
    )
)
async def show_tasks_list(message: Message, state: FSMContext):
    """
    Обработчик кнопки Посмотреть доступные ачивки.
    Отправляет список открытых ачивок, сохраняет открытые
    ачивки и их id через Data.
    """
    try:
        user = select_user(message.from_user.id)
        language = user.language
        lexicon = LEXICON[language]
        tasks = available_achievements(user.id, user.score)
        info = process_next_achievements(
            tasks=tasks, lexicon=lexicon, page_size=Pagination.page_size
        )
        msg = info["msg"]
        task_ids = info["task_ids"]
        task_info = info["task_info"]
        final_item = task_info["final_item"]
        await state.update_data(
            tasks=task_ids, task_info=task_info, language=language
        )
        await state.set_state(Data.tasks)
        await message.answer(
            msg,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_list_keyboard(len(tasks), end=final_item)
            ),
        )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при отправке списка ачивок. {err}")


@child_router.callback_query(F.data == "available_achievements")
async def show_tasks_list_inline(query: CallbackQuery, state: FSMContext):
    """
    Обработчик инлайн кнопки Посмотреть доступные ачивки.
    Отправляет список открытых ачивок, сохраняет открытые
    ачивки и их id через Data.
    """
    try:
        await query.answer()
        user = select_user(query.from_user.id)
        language = user.language
        lexicon = LEXICON[language]
        tasks = available_achievements(user.id, user.score)
        info = process_next_achievements(
            tasks=tasks, lexicon=lexicon, page_size=Pagination.page_size
        )
        msg = info["msg"]
        task_ids = info["task_ids"]
        task_info = info["task_info"]
        final_item = task_info["final_item"]
        await state.update_data(
            tasks=task_ids, task_info=task_info, language=language
        )
        await state.set_state(Data.tasks)
        await query.message.edit_text(
            msg,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_list_keyboard(len(tasks), end=final_item)
            ),
        )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при отправке списка ачивок. {err}")


@child_router.callback_query(F.data == "next")
async def process_next_tasks(query: CallbackQuery, state: FSMContext):
    """
    Обработчик-пагинатор кнопки next. Достает инфу из машины
    состояний без запроса к базе.
    """
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        tasks = data["task_info"]["tasks"]
        count = data["task_info"]["count"]
        previous_final_item = data["task_info"]["final_item"]
        info = process_next_achievements(
            tasks=tasks,
            lexicon=lexicon,
            count=count,
            previous_final_item=previous_final_item,
            page_size=Pagination.page_size,
        )
        msg = info["msg"]
        task_ids = info["task_ids"]
        task_info = info["task_info"]
        final_item = task_info["final_item"]
        await state.update_data(tasks=task_ids, task_info=task_info)
        await state.set_state(Data.tasks)
        await query.message.edit_text(
            msg,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_list_keyboard(
                    len(tasks), previous_final_item, final_item
                )
            ),
        )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при обработке next. {err}")


@child_router.callback_query(F.data == "previous")
async def process_previous_tasks(query: CallbackQuery, state: FSMContext):
    """
    Обработчик-пагинатор кнопки previous. Достает инфу из машины
    состояний без запроса к базе.
    """
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        tasks = data["task_info"]["tasks"]
        count = data["task_info"]["count"]
        previous_final_item = data["task_info"]["final_item"]
        info = process_previous_achievements(
            tasks=tasks,
            lexicon=lexicon,
            count=count,
            previous_final_item=previous_final_item,
            page_size=Pagination.page_size,
        )
        msg = info["msg"]
        task_ids = info["task_ids"]
        task_info = info["task_info"]
        first_item = task_info["first_item"]
        final_item = task_info["final_item"]
        await state.update_data(tasks=task_ids, task_info=task_info)
        await state.set_state(Data.tasks)
        await query.message.edit_text(
            msg,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_list_keyboard(
                    len(tasks), first_item, final_item
                )
            ),
        )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при обработке previous. {err}")


@child_router.callback_query(F.data == "info")
async def process_info_button(query: CallbackQuery):
    await query.answer()
    pass


# Обработчики выбора и выполнения ачивки
@child_router.callback_query(Data.tasks)
@child_router.callback_query(
    F.data.in_([str(x) for x in range(Pagination.achievements_num)])
)
async def show_task(query: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопок выбора отдельной ачивки.
    Получаем условный id ачивки из callback_data, достаем реальный id из
    состояние Data и получаем полную инфу об ачивке из базы данных.
    """
    try:
        await query.answer()
        data = await state.get_data()
        if not data:
            user = select_user(query.from_user.id)
            await query.message.answer(
                LEXICON[user.language]["error_getting_achievement"],
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=task_keyboard(user.language)
                ),
            )
            return
        language = data["language"]
        lexicon = LEXICON[language]
        task_number = int(query.data)
        # Достаем id ачивки из состояния и делаем запрос к базе
        task_id = data["tasks"][task_number]
        task_info = get_achievement_info(task_id, lexicon)
        info = task_info["info"]
        image = task_info["image"]
        msg = (
            f'{lexicon["achievement_chosen"]}\n\n'
            f"{info}\n\n"
            f'{lexicon["send_artifact"]}'
        )
        await state.update_data(task_id=task_id)
        await state.set_state(Data.artifact)
        if not image:
            await query.message.answer(
                msg,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=task_keyboard(language)
                ),
            )
            return
        await query.message.answer_photo(
            photo=image,
            caption=msg,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_keyboard(language)
            ),
        )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при получении ачивки: {err}")


@child_router.message(Data.artifact)
@child_router.message(Data.artifact, F.media_group_id)
async def process_artefact(
    message: Message, state: FSMContext, bot: Bot, album: dict, media_group
):
    """
    Обработчик артефактов, файлов, которые отправляет ребенок.
    """
    try:
        # Достаем id профиля вожатого в тг из базы
        data = await state.get_data()
        task_id = data["task_id"]
        language = data["language"]
        lexicon = LEXICON[language]
        councelors = get_users_by_role("councelor")
        councelor = (
            councelors[0] if councelors else select_user(message.from_user.id)
        )
        if media_group:
            status_changed = await process_artifact_group(
                album, task_id, lexicon
            )
        else:
            status_changed = await process_artifact(message, task_id, lexicon)
        if not status_changed:
            await state.set_state(Data.artifact)
            return
        elif status_changed:
            await bot.send_message(
                chat_id=councelor.id,
                text=LEXICON[councelor.language]["new_artifact"],
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=art_list_keyboard(councelor.language),
                    resize_keyboard=True,
                    one_time_keyboard=True,
                ),
            )
        await message.answer(
            lexicon["artifact_sent"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_keyboard(language)
            ),
        )
        await state.clear()
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при обработке артефакта: {err}")


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
async def edit_profile(message: Message, state: FSMContext):
    """Обработчик для редактирования профиля ребенка."""
    try:
        await state.clear()
        user = select_user(message.chat.id)
        await message.answer(
            LEXICON[user.language]["edit_profile"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=edit_profile_keyboard(user.language)
            ),
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
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=edit_profile_keyboard(user.language)
            ),
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
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=choose_language_keyboard
            ),
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
        await query.message.answer(
            LEXICON[language]["language_changed"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=edit_profile_keyboard(language)
            ),
        )
    except KeyError as err:
        logger.error(f"Ошибка в ключевом слове при изменении языка: {err}")
    except Exception as err:
        logger.error(f"Ошибка при изменении языка: {err}")

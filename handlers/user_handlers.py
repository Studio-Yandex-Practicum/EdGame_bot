import logging

from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    CallbackQuery,
    ReplyKeyboardRemove,
)
from aiogram.filters import CommandStart, Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.keyboards import (
    menu_keyboard,
    profile_keyboard,
    edit_profile_keyboard,
    choose_language_keyboard,
    task_list_keyboard,
    task_keyboard,
    create_welcome_keyboard,
    contacts_keyboard,
    help_keyboard,
)
from keyboards.set_menu import set_main_menu
from keyboards.methodist_keyboards import (
    art_list_keyboard,
    methodist_profile_keyboard,
)
from lexicon.lexicon import LEXICON, LEXICON_COMMANDS
from .artifact_handlers import process_artifact
from utils.db_commands import (
    register_user,
    select_user,
    set_user_param,
    available_achievements,
    get_achievement,
    get_all_achievements,
    get_users_by_role,
    user_achievements,
)
from utils.utils import (
    process_next_achievements,
    process_previous_achievements,
)
from db.engine import session
from .methodist_handlers import methodist_router

logger = logging.getLogger(__name__)

router = Router()
child_router = Router()
router.include_routers(child_router, methodist_router)

# Количество ачивок на странице ачивок
PAGE_SIZE = 2
# Количество возможных кнопок
ACHIEVEMENTS_NUM = len(get_all_achievements())


class Data(StatesGroup):
    """
    Машина состояний для реализации сценариев диалогов с пользователем.
    """

    name = State()
    language = State()
    change_name = State()
    change_bio = State()
    change_language = State()
    task_id = State()
    tasks = State()
    tasks_info = State()
    artifact = State()


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
        await message.answer(text=LEXICON["EN"]["councelor"])


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message):
    # Сохраняем пользователя в БД, роль по умолчанию 'kid'
    register_user(message)
    await message.answer(
        text=f"{LEXICON_COMMANDS['/start']}",
        reply_markup=create_welcome_keyboard(),
    )


# Этот хендлер срабатывает на апдейт CallbackQuery с выбором языка
@router.callback_query(Text(text=["ru_pressed", "tt_pressed", "en_pressed"]))
async def process_buttons_press(callback):
    user = select_user(callback.from_user.id)
    if callback.data == "ru_pressed":
        user.language = "RU"
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
    try:
        user = select_user(message.chat.id)
        language = user.language
        lexicon = LEXICON[language]
        set_user_param(user, name=message.text)
        await state.clear()
        await message.answer(
            f'{lexicon["hello"]}, {user.name}! ' f'{lexicon["hello_message"]}',
            reply_markup=ReplyKeyboardMarkup(
                keyboard=menu_keyboard(language),
                resize_keyboard=True,
                one_time_keyboard=True,
            ),
        )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при отправке сообщения с меню. {err}")


@child_router.message(Command(commands="help"))
@child_router.message(
    F.text.regexp(r"^Справка по работе бота$")
    | F.text.regexp(r"^Instructions on how to use the bot$")
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


@child_router.message(F.text.regexp(r"^Доступные задания$"))
@child_router.message(F.text.regexp(r"^Available achievements$"))
@child_router.message(Command(commands="achievements"))
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
        info = process_next_achievements(tasks=tasks, page_size=PAGE_SIZE)
        text = info[0]
        task_ids = info[1]
        task_info = info[2]
        final_item = task_info["final_item"]
        await state.update_data(
            tasks=task_ids, task_info=task_info, language=language
        )
        await state.set_state(Data.tasks)
        await message.answer(
            f'{lexicon["available_achievements"]}:\n\n'
            f"{text}\n\n"
            f'{lexicon["choose_achievement"]}:',
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
        info = process_next_achievements(tasks=tasks, page_size=PAGE_SIZE)
        text = info[0]
        task_ids = info[1]
        task_info = info[2]
        final_item = task_info["final_item"]
        await state.update_data(
            tasks=task_ids, task_info=task_info, language=language
        )
        await state.set_state(Data.tasks)
        await query.message.edit_text(
            f'{lexicon["available_achievements"]}:\n\n'
            f"{text}\n\n"
            f'{lexicon["choose_achievement"]}:',
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
            count=count,
            previous_final_item=previous_final_item,
            page_size=PAGE_SIZE,
        )
        text = info[0]
        task_ids = info[1]
        task_info = info[2]
        final_item = task_info["final_item"]
        await state.update_data(tasks=task_ids, task_info=task_info)
        await state.set_state(Data.tasks)
        await query.message.edit_text(
            f'{lexicon["available_achievements"]}:\n\n'
            f"{text}\n\n"
            f'{lexicon["choose_achievement"]}:',
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
            count=count,
            previous_final_item=previous_final_item,
            page_size=PAGE_SIZE,
        )
        text = info[0]
        task_ids = info[1]
        task_info = info[2]
        first_item = task_info["first_item"]
        final_item = task_info["final_item"]
        await state.update_data(tasks=task_ids, task_info=task_info)
        await state.set_state(Data.tasks)
        await query.message.edit_text(
            f'{lexicon["available_achievements"]}:\n\n'
            f"{text}\n\n"
            f'{lexicon["choose_achievement"]}:',
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
    pass


@child_router.callback_query(Data.tasks)
@child_router.callback_query(
    F.data.in_([str(x) for x in range(ACHIEVEMENTS_NUM)])
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
        task = get_achievement(task_id)
        name = task.name
        image = task.image
        description = task.description
        instruction = task.instruction
        artifact_type = task.artifact_type
        task_type = task.achievement_type
        score = task.score
        price = task.price
        info = (
            f'{lexicon["task_name"]}: {name}\n'
            f'{lexicon["score_rate"]}: {score}\n'
            f'{lexicon["task_description"]}: {description}\n'
            f'{lexicon["task_instruction"]}: {instruction}\n'
            f'{lexicon["artifact_type"]}: {artifact_type}\n'
            f'{lexicon["task_type"]}: {task_type}\n'
            f'{lexicon["task_price"]}: {price}'
        )
        msg = (
            f'{lexicon["achievement_chosen"]}\n\n'
            f"{info}\n\n"
            f'{lexicon["send_artifact"]}'
        )
        await state.update_data(task_id=task_id)
        await state.set_state(Data.artifact)
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
async def process_artefact(message: Message, state: FSMContext, bot: Bot):
    """
    Обработчик артефактов, файлов, которые отправляет ребенок.
    """
    try:
        # Достаем id профиля преподавателя в тг из базы
        data = await state.get_data()
        task_id = data["task_id"]
        language = data["language"]
        councelors = get_users_by_role("councelor")
        councelor = (
            councelors[0] if councelors else select_user(message.from_user.id)
        )
        await state.clear()
        status_changed = await process_artifact(message, task_id)
        if status_changed:
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
            LEXICON[language]["artifact_sent"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_keyboard(language)
            ),
        )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при обработке артефакта: {err}")


@child_router.message(Command(commands="current_achievements"))
@child_router.message(F.text.regexp(r"^Текущие задания$"))
@child_router.message(F.text.regexp(r"^Current achievements$"))
async def show_current_tasks(message: Message):
    """
    Показывам ачивки в статусе на проверке либо предлагаем
    перейти к списку ачивок.
    """
    try:
        # Достаем из базы ачивки со статусом на проверке
        user = select_user(message.from_user.id)
        lexicon = LEXICON[user.language]
        achievements = user_achievements(user.id)
        in_review = []
        count = 0
        for achievement in achievements:
            # Добавляем описания ачивок в список
            task = achievement[0]
            status = achievement[1]
            if status == "pending":
                count += 1
                task_info = (
                    f'{count}: {lexicon["pending_councelor"]}\n'
                    f'{lexicon["task_name"]}: {task.name}\n'
                    f'{lexicon["task_description"]}: {task.description}'
                )
                in_review.append(task_info)
            if status == "pending_methodist":
                count += 1
                task_info = (
                    f'{count}: {lexicon["pending_methodist"]}\n'
                    f'{lexicon["task_name"]}: {task.name}\n'
                    f'{lexicon["task_description"]}: {task.description}'
                )
                in_review.append(task_info)
        text = "\n\n".join(in_review)
        msg = (
            f'{lexicon["achievements_completed"]}\n\n'
            f"{text}\n\n"
            f'{lexicon["cheer_up"]}'
        )
        if not in_review:
            msg = lexicon["no_achievement_completed"]
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


@child_router.message(Command(commands="reviewed_achievements"))
@child_router.message(F.text.regexp(r"^Проверенные задания$"))
@child_router.message(F.text.regexp(r"^Reviewed achievements$"))
async def show_reviewed_tasks(message: Message):
    """
    Показывам ачивки в статусе на проверке либо предлагаем
    перейти к списку ачивок.
    """
    try:
        # Достаем из базы ачивки со статусом на проверке
        user = select_user(message.from_user.id)
        lexicon = LEXICON[user.language]
        achievements = user_achievements(user.id)
        reviewed = []
        count = 0
        for achievement in achievements:
            # Добавляем описания ачивок в список
            task = achievement[0]
            status = achievement[1]
            rejection_reason = achievement[2]
            if status == "rejected":
                count += 1
                task_info = (
                    f'{count}: {lexicon["status_rejected"]}\n'
                    f'{lexicon["rejection_reason"]}: {rejection_reason}'
                    f'{lexicon["task_name"]}: {task.name}\n'
                    f'{lexicon["task_description"]}: {task.description}'
                )
                reviewed.append(task_info)
            if status == "approved":
                count += 1
                task_info = (
                    f'{count}: {lexicon["status_approved"]}\n'
                    f'{lexicon["task_name"]}: {task.name}\n'
                    f'{lexicon["task_description"]}: {task.description}'
                    f'{lexicon["score_added"]}: {task.score}'
                )
                reviewed.append(task_info)
        text = "\n\n".join(reviewed)
        msg = (
            f'{lexicon["achievements_completed"]}\n\n'
            f"{text}\n\n"
            f'{lexicon["cheer_up"]}'
        )
        if not reviewed:
            msg = lexicon["no_achievement_reviewed"]
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


@child_router.message(F.text.regexp(r"^Личный кабинет$"))
@child_router.message(F.text.regexp(r"^Profile$"))
@child_router.message(Command(commands="lk"))
async def profile_info(message: Message, state: FSMContext):
    """Обработчик показывает главное меню профиля студента."""
    try:
        await state.clear()
        # Достаем инфу о пользователе из базы
        user = select_user(message.chat.id)
        lexicon = LEXICON[user.language]
        msg = (
            f'{lexicon["student_profile"]}\n\n'
            f'{lexicon["lk_info"]}:\n'
            f'{lexicon["name"]} - {user.name}\n'
            f'{lexicon["score"]} - {user.score}\n'
        )
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
        msg = (
            f'{lexicon["student_profile"]}\n\n'
            f'{lexicon["lk_info"]}:\n'
            f'{lexicon["name"]} - {user.name}\n'
            f'{lexicon["score"]} - {user.score}\n'
        )
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


@child_router.message(F.text.regexp(r"^Редактировать профиль$"))
@child_router.message(F.text.regexp(r"^Edit profile$"))
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
async def process_change_language(
    query: CallbackQuery, state: FSMContext, bot: Bot
):
    """Обработчик для изменения языка интерфейса."""
    try:
        await query.answer()
        await state.clear()
        user = select_user(query.from_user.id)
        # Изменяем язык бота на новый
        language = query.data
        set_user_param(user, language=language)
        # await set_main_menu(bot, language) меню удаляем в итоге
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


@child_router.message(F.text.regexp(r"^Написать вожатому$"))
@child_router.message(F.text.regexp(r"^Write to councelor$"))
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

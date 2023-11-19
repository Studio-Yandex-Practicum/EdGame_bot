import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.keyboards import (
    help_keyboard,
    pagination_keyboard,
    send_artifact_keyboard,
    task_keyboard,
    task_page_keyboard,
)
from keyboards.methodist_keyboards import art_list_keyboard
from lexicon.lexicon import BUTTONS, LEXICON
from utils.db_commands import (
    available_achievements,
    get_users_by_role_and_group,
    select_user,
)
from utils.pagination import PAGE_SIZE
from utils.states_form import Data
from utils.utils import (
    generate_achievement_message_for_kid,
    generate_achievements_list,
    generate_text_with_reviewed_tasks,
    generate_text_with_tasks_in_review,
    get_achievement_info,
    process_artifact,
    process_artifact_group,
)

logger = logging.getLogger(__name__)

child_task_router = Router()


@child_task_router.message(
    F.text.in_(
        [
            BUTTONS["RU"]["current_achievements"],
            BUTTONS["TT"]["current_achievements"],
            BUTTONS["EN"]["current_achievements"],
        ]
    )
)
async def show_current_tasks(message: Message, state: FSMContext):
    """
    Показывает ачивки в статусе на проверке.

    Если ачивок на проверке нет, предлагает перейти к списку ачивок.
    """
    try:
        # Достаем из базы ачивки со статусом на проверке
        user = select_user(message.from_user.id)
        lexicon = LEXICON[user.language]
        # Генерируем текст с инфой об ачивках
        msg = generate_text_with_tasks_in_review(user.id, lexicon)
        await message.answer(
            msg, reply_markup=task_keyboard(user.language, show_tasks=True)
        )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при получении текущих ачивок: {err}")


@child_task_router.message(
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
    Показывает ачивки в статусе одобрено или отклонено.

    Если проверенных ачивок нет, предлагает перейти к списку ачивок.
    """
    try:
        # Достаем из базы ачивки со статусом на проверке
        user = select_user(message.from_user.id)
        lexicon = LEXICON[user.language]
        # Генерируем текст с инфой об ачивках
        msg = generate_text_with_reviewed_tasks(user.id, lexicon)
        await message.answer(
            msg, reply_markup=task_keyboard(user.language, show_tasks=True)
        )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при получении проверенных ачивок: {err}")


# Обработчики списка ачивок и пагинации
@child_task_router.message(
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
        if not tasks:
            await message.answer(
                text=lexicon["no_available_achievements"],
                reply_markup=help_keyboard(language),
            )
            return
        info = generate_achievements_list(
            tasks=tasks, lexicon=lexicon, current_page=1, page_size=PAGE_SIZE
        )
        msg = info["msg"]
        task_ids = info["task_ids"]
        first_item = info["first_item"]
        final_item = info["final_item"]
        lk_button = {
            "text": BUTTONS[language]["lk"],
            "callback_data": "profile",
        }
        await state.set_state(Data.tasks)
        await state.update_data(
            tasks=tasks,
            task_ids=task_ids,
            pagination_info=info,
            language=language,
        )

        await message.answer(
            msg,
            reply_markup=pagination_keyboard(
                buttons_count=len(tasks),
                start=first_item,
                end=final_item,
                cd="task",
                page_size=PAGE_SIZE,
                extra_button=lk_button,
            ),
        )
    except KeyError as err:
        logger.error(f"Ошибка в ключевом слове в списке ачивок ребенка: {err}")
    except Exception as err:
        logger.error(f"Ошибка в списке ачивок ребенка. {err}")


@child_task_router.callback_query(F.data == "available_achievements")
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
        if not tasks:
            await query.message.answer(
                text=lexicon["no_available_achievements"],
                reply_markup=help_keyboard(language),
            )
            return
        info = generate_achievements_list(
            tasks=tasks,
            lexicon=lexicon,
            current_page=1,
            page_size=PAGE_SIZE,
        )
        msg = info["msg"]
        task_ids = info["task_ids"]
        first_item = info["first_item"]
        final_item = info["final_item"]
        lk_button = {
            "text": BUTTONS[language]["lk"],
            "callback_data": "profile",
        }
        await state.set_state(Data.tasks)
        await state.update_data(
            tasks=tasks,
            task_ids=task_ids,
            pagination_info=info,
            language=language,
        )
        await query.message.edit_text(
            msg,
            reply_markup=pagination_keyboard(
                buttons_count=len(tasks),
                start=first_item,
                end=final_item,
                cd="task",
                page_size=PAGE_SIZE,
                extra_button=lk_button,
            ),
        )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при отправке списка ачивок. {err}")


@child_task_router.callback_query(
    F.data.in_(
        ["back_to_available_achievements", "task:next", "task:previous"]
    )
)
async def show_tasks_list_pagination(query: CallbackQuery, state: FSMContext):
    """
    Обработчик инлайн кнопки Посмотреть доступные ачивки.

    Отправляет список открытых ачивок, сохраняет открытые
    ачивки и их id через Data.
    """
    try:
        await query.answer()
        data = await state.get_data()
        tasks = data["tasks"]
        pagination_info = data["pagination_info"]
        current_page = pagination_info["current_page"]
        pages = pagination_info["pages"]
        language = data["language"]
        lexicon = LEXICON[language]
        if query.data == "back_to_available_achievements":
            user = select_user(query.from_user.id)
            tasks = available_achievements(user.id, user.score)
            pages = None
        if not tasks:
            await query.message.answer(
                text=lexicon["no_available_achievements"],
                reply_markup=help_keyboard(language),
            )
            return
        if query.data == "task:next":
            current_page += 1
        elif query.data == "task:previous":
            current_page -= 1
        info = generate_achievements_list(
            tasks=tasks,
            lexicon=lexicon,
            current_page=current_page,
            page_size=PAGE_SIZE,
            pages=pages,
        )
        msg = info["msg"]
        first_item = info["first_item"]
        final_item = info["final_item"]
        lk_button = {
            "text": BUTTONS[language]["lk"],
            "callback_data": "profile",
        }
        await state.set_state(Data.tasks)
        await state.update_data(pagination_info=info)
        if query.data == "back_to_available_achievements":
            # Если возвращаемся со страницы отдельной ачивки,
            # редактировать сообщение с фото нельзя
            await state.update_data(task_ids=info["task_ids"])
            await query.message.answer(
                msg,
                reply_markup=pagination_keyboard(
                    buttons_count=len(tasks),
                    start=first_item,
                    end=final_item,
                    cd="task",
                    page_size=PAGE_SIZE,
                    extra_button=lk_button,
                ),
            )
            await query.message.delete()
        else:
            await query.message.edit_text(
                msg,
                reply_markup=pagination_keyboard(
                    buttons_count=len(tasks),
                    start=first_item,
                    end=final_item,
                    cd="task",
                    page_size=PAGE_SIZE,
                    extra_button=lk_button,
                ),
            )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при отправке списка ачивок. {err}")


@child_task_router.callback_query(F.data == "task:info")
async def process_info_button(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(Data.tasks)


# Обработчики выбора и выполнения ачивки
@child_task_router.callback_query(Data.tasks, F.data.startswith("task:"))
@child_task_router.callback_query(
    F.data.startswith("back_to_chosen_achievement:")
)
async def show_task(query: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопок выбора отдельной ачивки.

    Получаем условный id ачивки из callback_data, достаем реальный id из
    состояния Data и получаем полную инфу об ачивке из базы данных.
    """
    try:
        await query.answer()
        data = await state.get_data()
        child = select_user(query.from_user.id)
        language = data["language"]
        lexicon = LEXICON[language]
        task_number = int(query.data.split(":")[-1])
        # Достаем id ачивки из состояния и делаем запрос к базе
        task_id = data["task_ids"][task_number]
        # Получаем текст для сообщения и изображение ачивки
        task_info = get_achievement_info(task_id, lexicon)
        info = task_info["info"]
        image = task_info["image"]
        task = task_info["task"]
        msg = generate_achievement_message_for_kid(
            lexicon=lexicon, text=info, user=child, achievement=task
        )
        markup = task_page_keyboard(language)
        if task.achievement_type == "teamwork":
            markup = task_page_keyboard(
                language, available=True if child.captain_of_team_id else False
            )
        await state.set_state(Data.fulfil_achievement)
        await state.update_data(
            task_id=task_id, query_id=task_number, child=child
        )
        if not image:
            await query.message.edit_text(msg, reply_markup=markup)
            return
        await query.message.answer_photo(
            photo=image, caption=msg, reply_markup=markup
        )
        await query.message.delete()
    except KeyError as err:
        logger.error(
            f"Проверь правильность ключевых слов при получении ачивки: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при получении ачивки: {err}")


@child_task_router.callback_query(
    Data.fulfil_achievement, F.data == "fulfil_achievement"
)
async def process_fulfil_achievement(query: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки Выполнить ачивку.

    Начинает сценарий сбора артефактов.
    """
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        query_id = data["query_id"]
        await state.set_state(Data.artifact)
        await query.message.answer(
            lexicon["send_artifact"],
            reply_markup=send_artifact_keyboard(language, cd=query_id),
        )
        await query.message.delete()
    except KeyError as err:
        logger.error(
            "Проверь правильность ключевых слов при запросе "
            f"артефактов: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при запросе артефактов: {err}")


@child_task_router.message(Data.artifact)
@child_task_router.message(Data.artifact, F.media_group_id)
async def process_artefact(
    message: Message, state: FSMContext, bot: Bot, album: dict, media_group
):
    """Обработчик артефактов, файлов, которые отправляет ребенок."""
    try:
        # Достаем id профиля вожатого в тг из базы
        data = await state.get_data()
        child = data["child"]
        task_id = data["task_id"]
        language = data["language"]
        lexicon = LEXICON[language]
        query_id = data["query_id"]
        counsellors = get_users_by_role_and_group(
            role="counsellor", group=child.group
        )
        # пока нет реальных пользователей вожатых подставляем свой id
        counsellor = counsellors[0] if counsellors else None
        if media_group:
            status_changed = await process_artifact_group(
                messages=album,
                achievement_id=task_id,
                lexicon=lexicon,
                user=child,
            )
        else:
            status_changed = await process_artifact(
                message=message,
                achievement_id=task_id,
                lexicon=lexicon,
                user=child,
            )
        if not status_changed:
            await message.answer(
                lexicon["error_sending_artifact"],
                reply_markup=send_artifact_keyboard(language, cd=query_id),
            )
            await state.set_state(Data.artifact)
            return
        tasks = available_achievements(child.id, child.score)
        await state.update_data(tasks=tasks)
        await message.answer(
            lexicon["artifact_sent"],
            reply_markup=task_page_keyboard(language, available=False),
        )
        if counsellor:
            await bot.send_message(
                chat_id=counsellor.id,
                text=LEXICON[counsellor.language]["new_artifact"],
                reply_markup=art_list_keyboard(counsellor.language),
            )
    except KeyError as err:
        logger.error(
            "Проверь правильность ключевых слов при ообработке "
            f"артефакта: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при обработке артефакта: {err}")

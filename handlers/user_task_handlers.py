import logging
from aiogram import types

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.keyboards import pagination_keyboard, task_keyboard
from keyboards.methodist_keyboards import art_list_keyboard
from lexicon.lexicon import LEXICON, BUTTONS
from aiogram_inline_paginations.paginator import Paginator
from utils.db_commands import (
    select_user, available_achievements, get_users_by_role)
from utils.states_form import Data
from utils.utils import (
    generate_achievements_list, process_artifact,
    generate_text_with_tasks_in_review,
    generate_text_with_reviewed_tasks,
    get_achievement_info, process_artifact_group)
from utils.utils import (
    generate_achievements_list, process_artifact,
    generate_text_with_tasks_in_review,
    generate_text_with_reviewed_tasks,
    get_achievement_info, process_artifact_group)
from utils.user_utils import (get_category_child_all, 
                              get_category_id_achievement_all)
from utils.pagination import PAGE_SIZE
from db.engine import session

logger = logging.getLogger(__name__)

child_task_router = Router()


@child_task_router.message(
    F.text.in_(
        [BUTTONS["RU"]["current_achievements"],
         BUTTONS["TT"]["current_achievements"],
         BUTTONS["EN"]["current_achievements"]]))
async def show_current_tasks(message: Message, state: FSMContext):
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
            reply_markup=task_keyboard(user.language, show_tasks=True)
        )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при получении текущих ачивок: {err}")


@child_task_router.message(
    F.text.in_(
        [BUTTONS["RU"]["reviewed_achievements"],
         BUTTONS["TT"]["reviewed_achievements"],
         BUTTONS["EN"]["reviewed_achievements"]]))
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
            reply_markup=task_keyboard(user.language, show_tasks=True)
        )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при получении проверенных ачивок: {err}")


# Обработчики списка ачивок и пагинации
@child_task_router.message(
    F.text.in_(
        [BUTTONS["RU"]["available_achievements"],
         BUTTONS["TT"]["available_achievements"],
         BUTTONS["EN"]["available_achievements"]]))
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
            await message.answer(text='Нет доступных заданий.',
                                 reply_markup=task_keyboard(user.language,
                                                            show_tasks=True))
        else:
            info = generate_achievements_list(
                tasks=tasks,
                lexicon=lexicon,
                current_page=1,
                page_size=PAGE_SIZE)
            msg = info["msg"]
            task_ids = info["task_ids"]
            first_item = info["first_item"]
            final_item = info["final_item"]
            lk_button = {
                "text": BUTTONS[language]["lk"],
                "callback_data": "profile"
            }
            await state.set_state(Data.tasks)
            await state.update_data(
                tasks=tasks,
                task_ids=task_ids,
                pagination_info=info,
                language=language
            )

            await message.answer(
                msg,
                reply_markup=pagination_keyboard(
                    buttons_count=len(tasks),
                    start=first_item,
                    end=final_item,
                    cd='task',
                    page_size=PAGE_SIZE,
                    extra_button=lk_button)
            )
    except KeyError as err:
        logger.error(
            f"Ошибка в ключевом слове в списке ачивок ребенка: {err}")
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
            await query.message.answer(text='Нет доступных заданий.',
                                       reply_markup=task_keyboard(user.language,
                                                                  show_tasks=True))
        else:
            info = generate_achievements_list(
                tasks=tasks,
                lexicon=lexicon,
                current_page=1,
                page_size=PAGE_SIZE)
            msg = info["msg"]
            task_ids = info["task_ids"]
            first_item = info["first_item"]
            final_item = info["final_item"]
            lk_button = {
                "text": BUTTONS[language]["lk"],
                "callback_data": "profile"
            }
            await state.set_state(Data.tasks)
            await state.update_data(
                tasks=tasks,
                task_ids=task_ids,
                pagination_info=info,
                language=language
            )
            await query.message.edit_text(
                msg,
                reply_markup=pagination_keyboard(
                    buttons_count=len(tasks),
                    start=first_item,
                    end=final_item,
                    cd='task',
                    page_size=PAGE_SIZE,
                    extra_button=lk_button)
            )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при отправке списка ачивок. {err}")


@child_task_router.callback_query(
    F.data.in_(
        ["back_to_available_achievements", "task:next", "task:previous"]))
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
        language = data["language"]
        lexicon = LEXICON[language]
        pagination_info = data["pagination_info"]
        current_page = pagination_info["current_page"]
        pages = pagination_info["pages"]
        if query.data == 'back_to_available_achievements':
            user = select_user(query.from_user.id)
            tasks = available_achievements(user.id, user.score)
            pages = None
        if query.data == 'task:next':
            current_page += 1
        elif query.data == 'task:previous':
            current_page -= 1
        info = generate_achievements_list(
            tasks=tasks,
            lexicon=lexicon,
            current_page=current_page,
            page_size=PAGE_SIZE,
            pages=pages)
        msg = info["msg"]
        first_item = info['first_item']
        final_item = info["final_item"]
        lk_button = {
            "text": BUTTONS[language]["lk"],
            "callback_data": "profile"
        }
        await state.set_state(Data.tasks)
        await state.update_data(pagination_info=info)
        if query.data == 'back_to_available_achievements':
            # Если возвращаемся со страницы отдельной ачивки,
            # редактировать сообщение с фото нельзя
            await query.message.answer(
                msg,
                reply_markup=pagination_keyboard(
                    buttons_count=len(tasks),
                    start=first_item,
                    end=final_item,
                    cd='task',
                    page_size=PAGE_SIZE,
                    extra_button=lk_button)
            )
            await query.message.delete()
        else:
            await query.message.edit_text(
                msg,
                reply_markup=pagination_keyboard(
                    buttons_count=len(tasks),
                    start=first_item,
                    end=final_item,
                    cd='task',
                    page_size=PAGE_SIZE,
                    extra_button=lk_button)
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
@child_task_router.callback_query(Data.tasks, F.data.startswith('task'))
async def show_task(query: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопок выбора отдельной ачивки.
    Получаем условный id ачивки из callback_data, достаем реальный id из
    состояние Data и получаем полную инфу об ачивке из базы данных.
    """
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        task_number = int(query.data.split(':')[-1])
        # Достаем id ачивки из состояния и делаем запрос к базе
        task_id = data["task_ids"][task_number]
        # Получаем текст для сообщения и изображение ачивки
        task_info = get_achievement_info(task_id, lexicon)
        info = task_info["info"]
        image = task_info["image"]
        msg = (
            f'{lexicon["achievement_chosen"]}\n\n'
            f"{info}\n\n"
            f'{lexicon["send_artifact"]}'
        )
        await state.set_state(Data.artifact)
        await state.update_data(task_id=task_id, query_id=task_number)
        if not image:
            await query.message.edit_text(
                msg,
                reply_markup=task_keyboard(language)
            )
            return
        await query.message.answer_photo(
            photo=image,
            caption=msg,
            reply_markup=task_keyboard(language)
        )
        await query.message.delete()
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при получении ачивки: {err}")


@child_task_router.message(Data.artifact)
@child_task_router.message(Data.artifact, F.media_group_id)
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
            await message.answer(
                lexicon["error_getting_achievement"],
                reply_markup=task_keyboard(language))
            await state.set_state(Data.artifact)
            return
        elif status_changed:
            await bot.send_message(
                chat_id=councelor.id,
                text=LEXICON[councelor.language]["new_artifact"],
                reply_markup=art_list_keyboard(councelor.language)
            )
        await message.answer(
            lexicon["artifact_sent"],
            reply_markup=task_keyboard(language)
        )
    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при обработке артефакта: {err}")


@child_task_router.message(F.text.in_([BUTTONS["RU"]["category"]]))
async def process_artefact(message: Message, state: FSMContext):
    print(10)
    try:
        category = get_category_child_all(session)
        print(11, category)
        if len(category) == 0:
           
            await message.answer(LEXICON["RU"]['no_category'])
        buttons = []
        print(12)
        for i in range(len(category)):
            t = category[i]
            print(t, 13)
            button = InlineKeyboardButton(
                text=t.name, callback_data=f'{t.id}')
            print(14)
            buttons.append([button])
        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await state.set_state(Data.category)
        await message.answer(LEXICON["RU"]["choose_achievement"],  
                             reply_markup=reply_markup)
    except Exception:
        await message.answer(LEXICON["RU"]["error_achievement"])
    finally:
        session.close()


@child_task_router.callback_query(Data.category)
async def check_child_buttons(query: CallbackQuery, state: FSMContext):
    print(1123)
    try:
        category_id = int(query.data[0])
        print(category_id, 0)
        achievements = get_category_id_achievement_all(session, category_id)
        print(achievements)
        result = ""
        for achievement in achievements:
            result += f"{achievement.name}\n"
            print(result)
        await query.message.answer(result)
    except Exception:
        await query.message.answer(LEXICON["RU"]["error_achievements"])
    finally:
        session.close()
    
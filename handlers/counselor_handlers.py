from aiogram import F, Router, types
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram_inline_paginations.paginator import Paginator
from db.engine import session
from db.models import AchievementStatus, User
from keyboards.counselor_keyboard import (
    create_inline_keyboard,
    create_profile_keyboard,
    create_yes_no_keyboard,
)
from utils.db_commands import (
    approve_task,
    available_achievements,
    reject_task,
    send_to_methdist,
)
from utils.user_utils import (
    get_achievement_description,
    get_achievement_file_id,
    get_achievement_file_type,
    get_achievement_instruction,
    get_achievement_name,
    get_achievement_status_by_id,
    get_achievements_by_name,
    get_all_child_achievements,
    get_all_children,
    get_all_children_from_group,
    get_child_by_name_and_group,
    get_message_text,
    get_user_name,
    save_rejection_reason_in_db,
    send_task,
)
from lexicon.lexicon import LEXICON, BUTTONS

router = Router()


class TaskState(StatesGroup):
    """
    Машина состояний для реализации сценариев диалогов с вожатым.
    """

    group = State()
    user_id = State()
    task_id = State()
    child_id = State()
    child_info = State()
    child_name = State()
    reject_message = State()
    children_group = State()
    achievement_name = State()
    group_buttons = State()


@router.message(Command("lk"))
async def enter_profile(message: types.Message):
    keyboard = create_profile_keyboard()
    await message.answer("Теперь ты в личном кабинете!", reply_markup=keyboard)


@router.message(Text("Список детей"))
async def show_children_list(message: types.Message):
    try:
        children = get_all_children(session)

        children_text = "\n".join(
            [f"Имя: {child.name} - Очки: {child.score}" for child in children]
        )
        await message.answer(f"Список детей:\n{children_text}")
    except Exception:
        await message.answer("Произошла ошибка при получении списка детей.")
    finally:
        session.close()


@router.message(Text("Проверить задания"))
async def check_requests(message: types.Message):
    children = session.query(User).filter(User.role == "kid").all()
    try:
        for child in children:
            tasks = (
                session.query(AchievementStatus)
                .filter(
                    AchievementStatus.user_id == child.id,
                    AchievementStatus.status == "pending",
                )
                .all()
            )

            for task in tasks:
                name = get_achievement_name(session, task.achievement_id)
                description = get_achievement_description(
                    session, task.achievement_id
                )
                instruction = get_achievement_instruction(
                    session, task.achievement_id
                )

                file_id = get_achievement_file_id(session, task.achievement_id)
                file_type = get_achievement_file_type(
                    session, task.achievement_id
                )
                message_text = get_message_text(session, task.id)
                inline_keyboard = create_inline_keyboard(task.id, child.name)

                caption = (
                    f"Задание на проверку от {child.name}\n\n"
                    f"Название задания: {name}\n\n"
                    f"Описание задания: {description}\n\n"
                    f"Инструкция: {instruction}"
                )
                await send_task(
                    message,
                    file_type,
                    file_id,
                    caption,
                    message_text,
                    inline_keyboard,
                )
    except Exception:
        await message.answer("Произошла ошибка при поиске заданий.")
    finally:
        session.close()


@router.callback_query(lambda c: c.data.startswith("accept:"))
async def approve_handler(callback_query: types.CallbackQuery):
    task_id = int(callback_query.data.split(":")[1])
    name = str(callback_query.data.split(":")[2])
    try:
        if approve_task(task_id):
            await callback_query.message.answer(f"Задание от {name} принято!")
        else:
            await callback_query.message.answer(
                f"Не удалось найти задание с ID {task_id}."
            )
    except Exception:
        await callback_query.message.answer(
            "Произошла ошибка при подтверждении задания."
        )
    finally:
        session.close()


@router.callback_query(lambda c: c.data.startswith("reject:"))
async def reject_handler(callback_query: types.CallbackQuery):
    task_id = int(callback_query.data.split(":")[1])
    name = str(callback_query.data.split(":")[2])
    try:
        if reject_task(task_id):
            inline_keyboard = create_yes_no_keyboard(task_id)
            await callback_query.message.answer(
                f"Задание от {name} отклонено! Хотите указать причину отказа?",
                reply_markup=inline_keyboard,
            )
        else:
            await callback_query.message.answer(
                f"Не удалось найти задание с ID {task_id}."
            )
    except Exception:
        await callback_query.message.answer(
            "Произошла ошибка при отклонении задания."
        )
    finally:
        session.close()


@router.callback_query(F.data == "yes_handler")
@router.callback_query(lambda c: c.data.startswith("yes:"))
async def yes_handler(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = int(callback_query.data.split(":")[1])
    try:
        await state.set_state(TaskState.reject_message)
        await state.set_data({"task_id": task_id})
        await callback_query.message.answer(
            "Введите причину отказа следующим сообщением. Если передумаете - введите 'Отмена'"
        )
    except Exception:
        await callback_query.message.answer(
            "Произошла ошибка при обработке запроса."
        )
    finally:
        session.close()


@router.callback_query(F.data == "no_handler")
@router.callback_query(lambda c: c.data.startswith("no:"))
async def no_handler(callback_query: types.CallbackQuery):
    try:
        await callback_query.message.answer(
            "Хорошо, задание будет отколонено без комментария"
        )
    except Exception:
        await callback_query.message.answer(
            "Произошла ошибка при обработке запроса."
        )
    finally:
        session.close()


@router.message(TaskState.reject_message)
async def rejection_reason(message: types.Message, state: FSMContext):
    task_data = await state.get_data()
    task_id = task_data.get("task_id")

    if message.text in ["Отмена", "Нет"]:
        await message.answer(
            "Хорошо, сообщение об отмене будет доставлено без комментария"
        )
        await state.clear()
        session.close()
        return
    save_rejection_reason_in_db(session, task_id, message.text)
    await message.answer("Причина отказа сохранена")
    await state.clear()
    session.close()


@router.callback_query(lambda c: c.data.startswith("back:"))
async def send_to_methodist(callback_query: types.CallbackQuery):
    task_id = int(callback_query.data.split(":")[1])
    name = str(callback_query.data.split(":")[2])
    if send_to_methdist(task_id):
        await callback_query.message.answer(
            f"Задание от {name} отправлено на проверку методисту"
        )


@router.message(Text("Проверить конкретное задание"))
async def display_task_review_requests(
    message: types.Message, state: FSMContext
):
    """Отображение всех входящих заявок на проверку одного задания"""
    await state.set_state(TaskState.achievement_name)
    await message.answer("Введите название задания, которое хотите проверить")


@router.message(TaskState.achievement_name)
async def display_task(message: types.Message, state: FSMContext):
    achievement_name = message.text
    try:
        achievement_id = get_achievements_by_name(session, achievement_name)
        name = get_achievement_name(session, achievement_id)
        description = get_achievement_description(session, achievement_id)
        instruction = get_achievement_instruction(session, achievement_id)
        file_type = get_achievement_file_type(session, achievement_id)
        await message.answer(
            f"Название задания: {name}\n\nОписание задания: {description}\n\nИнструкция к заданию: {instruction}"
        )
        achievements = get_achievement_status_by_id(session, achievement_id)
        for achievement in achievements:
            user_id = achievement.user_id
            file_id = get_achievement_file_id(
                session, achievement.achievement_id
            )
            message_text = achievement.message_text
            child = get_user_name(session, user_id)
            caption = f"Задание на проверку от {child}\n\n"
            inline_keyboard = create_inline_keyboard(achievement.id, child)
            await send_task(
                message,
                file_type,
                file_id,
                caption,
                message_text,
                inline_keyboard,
            )
            await state.clear()
    except Exception:
        await message.answer("Произошла ошибка при поиске задания")
        await state.clear()
    finally:
        session.close()


@router.message(Text("Узнать общий прогресс отряда"))
async def display_troop_progress(message: types.Message, state: FSMContext):
    """Возможность отображения общего прогресса отряда"""
    await state.set_state(TaskState.children_group)
    await message.answer(
        "Введите номер отряда по которому хотите получить информацию"
    )


@router.message(TaskState.children_group)
async def display_troop(message: types.Message, state: FSMContext):
    try:
        children = get_all_children_from_group(session, message.text)
        message_text = f"Общая численно отряда номер {message.text} составляет {len(children)} детей."
        score = sum(child.score for child in children)
        message_text += f"\n\nОбщий прогресс отряда - {score} баллов.\n"
        message_text += (
            "Вот имена детей из этого отряда и их персональный прогресс:\n"
        )
        children_info_list = [
            f"Имя: {child.name} - Очки: {child.score}" for child in children
        ]
        message_text += "\n\n".join(children_info_list)
        if len(children) != 0:
            await message.answer(message_text)
            await state.clear()
        else:
            raise Exception
    except Exception:
        await message.answer("Произошла ошибка при поиске отряда")
        await state.clear()
    finally:
        session.close()


@router.message(Text("Получить информацию о ребенке"))
async def check_child_info(message: types.Message, state: FSMContext):
    """Возможность проверки инфы о выбранном ребенке"""
    await state.set_state(TaskState.child_info)
    await message.answer(
        "Введите имя ребенка и номер отряда. Например: Иван Иванов 1"
    )


@router.message(TaskState.child_info)
async def check_child(message: types.Message, state: FSMContext):
    try:
        search_child = message.text.split(" ")
        name = f"{search_child[0]} {search_child[1]}"
        group = int(search_child[2])
        child = get_child_by_name_and_group(session, name, group)
        achievements = available_achievements(child.id, child.score)

        message_text = [
            f"Информация о ребенке по имени {name}:\n\nОчки: {child.score} Группа: {child.group}",
            "Доступные ачивки для ребенка:\n",
        ]
        message_text.extend(
            f"Название: {achievement.name}\nНеобходимо баллов: {achievement.price}\n"
            f"Вид: {achievement.achievement_type}\nБаллы за ачивку: {achievement.score}\n\n"
            for achievement in achievements
        )
        await message.answer("\n".join(message_text))
        await state.clear()
    except Exception:
        await message.answer("Произошла ошибка при поиске ребенка")
        await state.clear()
    finally:
        session.close()


@router.message(Text("Проверить задание конкретного ребенка"))
async def display_child_task_review_requests(
    message: types.Message, state: FSMContext
):
    """Отображение всех входящих заявок на проверку заданий одного ребёнка"""
    await state.set_state(TaskState.child_name)
    await message.answer(
        "Введите имя ребенка и номер отряда для проверки его заданий. Например: Иван Иванов 1"
    )


@router.message(TaskState.child_name)
async def display_child_task_review(message: types.Message, state: FSMContext):
    search_child = message.text.split(" ")
    try:
        name = f"{search_child[0]} {search_child[1]}"
        group = int(search_child[2])
        child_id = get_child_by_name_and_group(session, name, group).id
        achievements = get_all_child_achievements(session, child_id)
        if len(achievements) == 0:
            await message.answer("Ребенок пока не выполнил ни одного задания")

        for achievement in achievements:
            ac_id = achievement.achievement_id
            file_id = get_achievement_file_id(session, ac_id)
            message_text = achievement.message_text
            ac_name = get_achievement_name(session, ac_id)
            description = get_achievement_description(session, ac_id)
            instruction = get_achievement_instruction(session, ac_id)
            file_type = get_achievement_file_type(session, ac_id)
            inline_keyboard = create_inline_keyboard(achievement.id, name)
            caption = (
                f"Название задания: {ac_name}\n\n"
                f"Описание задания: {description}\n\n"
                f"Инструкция: {instruction}"
            )
            await send_task(
                message,
                file_type,
                file_id,
                caption,
                message_text,
                inline_keyboard,
            )
            await state.clear()
    except Exception:
        await message.answer("Произошла ошибка при ребенка")
        await state.clear()
    finally:
        session.close()


@router.message(Text("Проверить задание всего отряда"))
async def display_troop_task_review_requests(
    message: types.Message, state: FSMContext
):
    """Отображение всех входящих заявок на проверку заданий всего отряда"""
    await state.set_state(TaskState.group)
    await message.answer("Введите номер отряда для проверки всех заданий")


@router.message(TaskState.group)
async def display_troop_task_review(message: types.Message, state: FSMContext):
    try:
        user_ids = get_all_children_from_group(session, message.text)
        if len(user_ids) == 0:
            await message.answer("Такого отряда не существует")
        for user in user_ids:
            child_id = user.id
            achievements = get_all_child_achievements(session, child_id)
            child_name = get_user_name(session, child_id)
            for achievement in achievements:
                ac_id = achievement.achievement_id
                file_id = achievement.files_id
                message_text = achievement.message_text
                name = get_achievement_name(session, ac_id)
                description = get_achievement_description(session, ac_id)
                instruction = get_achievement_instruction(session, ac_id)
                file_type = get_achievement_file_type(session, ac_id)
                inline_keyboard = create_inline_keyboard(
                    achievement.id, child_name
                )
                caption = (
                    f"Задание на проверку от {child_name}\n\n"
                    f"Название задания: {name}\n\n"
                    f"Описание задания: {description}\n\n"
                    f"Инструкция: {instruction}"
                )
                await send_task(
                    message,
                    file_type,
                    file_id,
                    caption,
                    message_text,
                    inline_keyboard,
                )
                await state.clear()
    except Exception:
        await message.answer("Произошла ошибка при поиске отряда")
        await state.clear()
    finally:
        session.close()


@router.message(Text("Список детей в группе"))
async def show_children_group(message: types.Message):
    try:
        user_ids = get_all_children_from_group(session, message.text)
        if len(user_ids) == 0:
            await message.answer(LEXICON["RU"]["no_group"])
        markup = InlineKeyboardMarkup()
        for i in user_ids:
            markup.add(InlineKeyboardButton(f'{i[1]}',
                                            callback_data=
                                            f'name {i[0]}, {message.text}'))
            paginator = Paginator(data=markup, size=5)
            await TaskState.group_buttons
        await message.answer(LEXICON["RU"]["choose_child"],  reply_markup=paginator())
    except Exception:
        await message.answer(LEXICON["RU"]["error_group"])
    finally:
        session.close()


@router.callback_query(Text(startswith="name"))
async def check_child_buttons(call: types.CallbackQuery):
    try:
        action = call.data.split(",")
        name = action[0]
        group = action[1]
        child = get_child_by_name_and_group(session, name, group)
        achievements = available_achievements(child.id, child.score)

        message_text = [
            (f"Информация о ребенке по имени {name}:\n\nОчки:"
             f'{child.score} Группа: {child.group}"',
             "Доступные ачивки для ребенка:\n")
        ]
        message_text.extend(
            f"Название: {achievement.name}\nНеобходимо баллов: "
            f'{achievement.price}\n'
            f'Вид: {achievement.achievement_type}\nБаллы за ачивку:'
            f'{achievement.score}\n\n"'
            for achievement in achievements
        )
        await call.answer("\n".join(message_text))
    except Exception:
        await call.answer(LEXICON["RU"]["error_child"])
    finally:
        session.close()

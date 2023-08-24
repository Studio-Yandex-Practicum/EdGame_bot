from aiogram import F, Router, types
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db.engine import session
from db.models import AchievementStatus, User
from keyboards.keyboards import (
    create_inline_keyboard,
    create_profile_keyboard,
    create_yes_no_keyboard,
)
from utils.db_commands import approve_task, reject_task, send_to_methdist
from utils.user_utils import (
    get_achievement_description,
    get_achievement_file_id,
    get_achievement_instruction,
    get_achievement_name,
    save_rejection_reason_in_db,
    send_achievement_file,
)

router = Router()


class TaskState(StatesGroup):
    """
    Машина состояний для реализации сценариев диалогов с вожатым.
    """

    user_id = State()
    task_id = State()
    reject_message = State()


@router.message(Command("lk"))
async def enter_profile(message: types.Message):
    keyboard = create_profile_keyboard()
    await message.answer("Теперь ты в личном кабинете!", reply_markup=keyboard)


@router.message(Text("Список детей"))
async def show_children_list(message: types.Message):
    try:
        children = session.query(User).filter(User.role == "kid").all()
        children_text = "\n".join(
            [f"Имя: {child.name} - Очки: {child.score}" for child in children]
        )
        await message.answer(f"Список детей:\n{children_text}")
    except Exception as e:
        await message.answer("Произошла ошибка при получении списка детей.")
    finally:
        session.close()


@router.message(Text("Проверить задания"))
async def check_requests(message: types.Message):
    try:
        children = session.query(User).filter(User.role == "kid").all()

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
                achievement_name = get_achievement_name(session, task.achievement_id)
                achievement_description = get_achievement_description(
                    session, task.achievement_id
                )
                achievement_instruction = get_achievement_instruction(
                    session, task.achievement_id
                )
                achievement_file_id = get_achievement_file_id(
                    session, task.achievement_id
                )
                inline_keyboard = create_inline_keyboard(task.id)
                await send_achievement_file(
                    message,
                    child,
                    achievement_name,
                    achievement_description,
                    achievement_instruction,
                    achievement_file_id,
                    inline_keyboard,
                )
    except Exception as e:
        await message.answer("Произошла ошибка при проверке заданий.")
    finally:
        session.close()


@router.callback_query(lambda c: c.data.startswith("accept:"))
async def approve_handler(callback_query: types.CallbackQuery):
    task_id = int(callback_query.data.split(":")[1])
    try:
        if approve_task(task_id):
            await callback_query.message.answer(f"Задание с ID {task_id} принято!")
        else:
            await callback_query.message.answer(
                f"Не удалось найти задание с ID {task_id}."
            )
    except Exception as e:
        await callback_query.message.answer(
            f"Произошла ошибка при подтверждении задания."
        )
    finally:
        session.close()


@router.callback_query(lambda c: c.data.startswith("reject:"))
async def reject_handler(callback_query: types.CallbackQuery):
    task_id = int(callback_query.data.split(":")[1])
    try:
        if reject_task(task_id):
            inline_keyboard = create_yes_no_keyboard(task_id)
            await callback_query.message.answer(
                f"Задание с ID {task_id} отклонено! Хотите указать причину отказа?",
                reply_markup=inline_keyboard,
            )
        else:
            await callback_query.message.answer(
                f"Не удалось найти задание с ID {task_id}."
            )
    except Exception as e:
        await callback_query.message.answer(f"Произошла ошибка при отклонении задания.")
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
    except Exception as e:
        await callback_query.message.answer("Произошла ошибка при обработке запроса.")
    finally:
        session.close()


@router.message(state=TaskState.reject_message)
async def ejection_reason(message: types.Message, state: FSMContext):
    task_data = await state.get_data()
    task_id = task_data.get("task_id")
    try:
        if message.text != "Отмена":
            save_rejection_reason_in_db(session, task_id, message.text)
            await message.answer("Причина отказа сохранена")
    except Exception as e:
        await message.answer("Произошла ошибка при сохранении причины отказа.")
    finally:
        await message.answer(
            "Хорошо! Сообщение об отмене будет доставлено без комментария"
        )
        await state.clear()
        session.close()

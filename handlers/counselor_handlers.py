import base64

from aiogram import Router, types
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BufferedInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from db.engine import session
from db.models import AchievementStatus, User
from utils.user_utils import (
    change_achievement_status_by_id,
    get_achievement_description,
    get_achievement_image,
    get_achievement_instruction,
    get_achievement_name,
)

router = Router()


# Войти в личный кабинет
profile = KeyboardButton(text="Личный кабинет")

# Получить список детей и список заданий, отправленных на проверку
children_list = KeyboardButton(text="Список детей")
requests_inspection = KeyboardButton(text="Проверить задания")

# Кнопки в личном кабинете
profile_keyboard = [[children_list], [requests_inspection]]


@router.message(Command("lk"))
async def children_list(message: types.Message):
    keyboard = ReplyKeyboardMarkup(keyboard=profile_keyboard, resize_keyboard=True)
    await message.answer("Теперь ты в личном кабинете!", reply_markup=keyboard)


@router.message(Text("Список детей"))
async def children_list(message: types.Message):
    """Обработчик для команды получения списка детей."""
    children = session.query(User).filter(User.role == "kid").all()
    session.close()
    children_text = "\n".join(
        [f"Имя: {child.name} - Очки: {child.score}" for child in children]
    )

    await message.answer(f"Список детей:\n{children_text}")


@router.message(Text("Проверить задания"))
async def requests_inspection(message: types.Message, state: FSMContext):
    """Обработчик для команды получения списка заданий на проверку."""
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
            achievement_image = get_achievement_image(session, task.achievement_id)
            image_64_encode = base64.b64encode(achievement_image).decode("utf-8")
            image_bytes = base64.b64decode(image_64_encode)
            inline_keyboard = InlineKeyboardMarkup(
                row_width=1,
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Принять",
                            callback_data=f"accept:{task.id}",
                            width=2,
                        ),
                        InlineKeyboardButton(
                            text="Отклонить",
                            callback_data=f"reject:{task.id}",
                            width=2,
                        ),
                        InlineKeyboardButton(
                            text="Отправить на доп.проверку",
                            callback_data=f"back:{task.id}",
                            width=1,
                        ),
                    ]
                ],
            )

            await message.answer_photo(
                photo=BufferedInputFile(image_bytes, filename="image.jpg"),
                caption=f"Задание на проверку от {child.name}:\n{achievement_name} - {achievement_description} - {achievement_instruction}",
                reply_markup=inline_keyboard,
            )
    session.close()


@router.callback_query(lambda c: c.data.startswith("accept:"))
async def accept_handler(callback_query: types.CallbackQuery):
    """Обработчик для нажатия кнопки 'Принять'."""
    task_id = int(callback_query.data.split(":")[1])
    if change_achievement_status_by_id(session, task_id, "approved"):
        await callback_query.message.answer(f"Задание с ID {task_id} принято!")
    else:
        await callback_query.message.answer(f"Не удалось найти задание с ID {task_id}.")
    session.close()


@router.callback_query(lambda c: c.data.startswith("reject:"))
async def accept_handler(callback_query: types.CallbackQuery):
    """Обработчик для нажатия кнопки 'Отклонить'."""
    task_id = int(callback_query.data.split(":")[1])
    if change_achievement_status_by_id(session, task_id, "rejected"):
        await callback_query.message.answer(f"Задание с ID {task_id} отклонено!")
    else:
        await callback_query.message.answer(f"Не удалось найти задание с ID {task_id}.")
    session.close()


@router.callback_query(lambda c: c.data == "back")
async def back_handler(
    callback_query: types.CallbackQuery,
):  # TODO: надо придумать логику и реализовать метод
    """Обработчик для нажатия кнопки 'Отправить на доп.проверку'."""
    task_id = int(callback_query.data.split(":")[1])
    if change_achievement_status_by_id(session, task_id, "pending_methodist"):
        await callback_query.message.answer(
            f"Задание с ID {task_id} отправлено на проверку методисту!"
        )
    else:
        await callback_query.message.answer(f"Не удалось найти задание с ID {task_id}.")
    session.close()

import base64

from aiogram import Router, types
from aiogram.filters import Command, Text
from aiogram.types import (
    BufferedInputFile,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)
from db.engine import SessionLocal
from db.models import AchievementStatus, User
from utils.user_utils import (
    get_achievement_description,
    get_achievement_image,
    get_achievement_instruction,
    get_achievement_name,
)
from aiogram.fsm.context import FSMContext

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
    session = SessionLocal()
    children = session.query(User).filter(User.role == "kid").all()
    session.close()
    children_text = "\n".join(
        [f"Имя: {child.name} - Очки: {child.score}" for child in children]
    )

    await message.answer(f"Список детей:\n{children_text}")


@router.message(Text("Проверить задания"))
async def requests_inspection(message: types.Message):
    """Обработчик для команды получения списка заданий на проверку."""
    session = SessionLocal()
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
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Принять", callback_data=f"accept:{task.id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Отклонить", callback_data=f"reject:{task.id}"
                        )
                    ],
                ]
            )
            await message.answer_photo(
                photo=BufferedInputFile(image_bytes, filename="image.jpg"),
                caption=f"Задание на проверку от {child.name}:\n{achievement_name} - {achievement_description} - {achievement_instruction}",
                reply_markup=inline_keyboard,
            )
    session.close()


# @router.callback_query_handler(
#     lambda c: c.data.startswith("accept:") or c.data.startswith("reject:"),
#     state=TaskStates.choose_action,
# )
# async def process_accept_reject_callback(query: CallbackQuery, state: FSMContext):
#     task_id = int(query.data.split(":")[1])

#     async with state.proxy() as data:
#         data["task_id"] = task_id

#     await TaskStates.accept_task.set()
#     await query.answer("Вы уверены, что хотите принять задание?")


# @router.message_handler(
#     lambda message: message.text.lower() == "да", state=TaskStates.accept_task
# )
# async def accept_task(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         task_id = data["task_id"]
#         del data["task_id"]

#     session = SessionLocal()
#     update_achievement_status(session, task_id, message.from_user.id, "approved")
#     session.close()

#     await bot.send_message(message.from_user.id, "Задание принято!")

#     await state.finish()


# @dp.message_handler(
#     lambda message: message.text.lower() == "да", state=TaskStates.reject_task
# )
# async def reject_task(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         task_id = data["task_id"]
#         del data["task_id"]

#     session = SessionLocal()
#     update_achievement_status(session, task_id, message.from_user.id, "rejected")
#     session.close()

#     await bot.send_message(message.from_user.id, "Задание отклонено!")

#     await state.finish()

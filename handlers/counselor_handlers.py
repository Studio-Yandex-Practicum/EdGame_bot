import base64

from aiogram import Router, types
from aiogram.filters import Command, Text
from aiogram.types import BufferedInputFile

from db.engine import session
from db.models import AchievementStatus, User
from keyboards.keyboards import create_inline_keyboard, create_profile_keyboard
from utils.user_utils import (
    change_achievement_status_by_id,
    get_achievement_description,
    get_achievement_image,
    get_achievement_instruction,
    get_achievement_name,
)

router = Router()


@router.message(Command("lk"))
async def enter_profile(message: types.Message):
    keyboard = create_profile_keyboard()
    await message.answer("Теперь ты в личном кабинете!", reply_markup=keyboard)


@router.message(Text("Список детей"))
async def show_children_list(message: types.Message):
    children = session.query(User).filter(User.role == "kid").all()
    session.close()
    children_text = "\n".join(
        [f"Имя: {child.name} - Очки: {child.score}" for child in children]
    )
    await message.answer(f"Список детей:\n{children_text}")


@router.message(Text("Проверить задания"))
async def check_requests(message: types.Message):
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

            inline_keyboard = create_inline_keyboard(task.id)

            await message.answer_photo(
                photo=BufferedInputFile(image_bytes, filename="image.jpg"),
                caption=f"Задание на проверку от {child.name}:\n{achievement_name} - {achievement_description} - {achievement_instruction}",
                reply_markup=inline_keyboard,
            )

    session.close()


@router.callback_query(lambda c: c.data.startswith("accept:"))
async def accept_handler(callback_query: types.CallbackQuery):
    task_id = int(callback_query.data.split(":")[1])
    if change_achievement_status_by_id(session, task_id, "approved"):
        await callback_query.message.answer(f"Задание с ID {task_id} принято!")

    else:
        await callback_query.message.answer(f"Не удалось найти задание с ID {task_id}.")
    session.close()


@router.callback_query(lambda c: c.data.startswith("reject:"))
async def reject_handler(callback_query: types.CallbackQuery):
    task_id = int(callback_query.data.split(":")[1])
    if change_achievement_status_by_id(session, task_id, "rejected"):
        await callback_query.message.answer(f"Задание с ID {task_id} отклонено!")
    else:
        await callback_query.message.answer(f"Не удалось найти задание с ID {task_id}.")
    session.close()


@router.callback_query(lambda c: c.data.startswith("back"))
async def back_handler(callback_query: types.CallbackQuery):
    task_id = int(callback_query.data.split(":")[1])
    if change_achievement_status_by_id(session, task_id, "pending_methodist"):
        await callback_query.message.answer(
            f"Задание с ID {task_id} отправлено на проверку методисту!"
        )
    else:
        await callback_query.message.answer(f"Не удалось найти задание с ID {task_id}.")
    session.close()

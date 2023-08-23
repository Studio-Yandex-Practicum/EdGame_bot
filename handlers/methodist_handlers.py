import logging

from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove,
    InlineKeyboardMarkup)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from lexicon.lexicon import LEXICON
from keyboards.keyboards import task_list_keyboard
from keyboards.methodist_keyboards import methodist_profile_keyboard
from utils.db_commands import get_all_achievements, select_user

logger = logging.getLogger(__name__)

methodist_router = Router()


class Data(StatesGroup):
    task_for_review = State()
    task_ids = State()
    tasks_to_edit = State()


@methodist_router.message(F.text.regexp(r'^Задания на проверку$'))
async def show_tasks_for_review(message: Message, state: FSMContext):
    '''
    Обработчик кнопки Задания на проверку. Показывает ачивки,
    отправленные методисту на проверку в статусе "pending_methodist".
    '''
    try:
        user = select_user(message.from_user.id)
        language = user.language
        lexicon = LEXICON[language]
        tasks_for_review = get_all_achievements(status='pending_methodist')
        task_list = []
        task_ids = {}
        count = 0
        for achievement_status in tasks_for_review:
            user = achievement_status[0]
            achievement = achievement_status[1]
            count += 1
            info = (
                f'{count}: {achievement.name}\n'
                f'{lexicon["sender"]}: {user.name}\n')
            task_list.append(info)
            task_ids[str(count)] = achievement_status[2].id
        text = '\n\n'.join(task_list)
        msg = (
            f'{lexicon["children_tasks"]}:\n\n'
            f'{text}\n\n'
            f'{lexicon["checkout_artifacts"]}:')
        await state.update_data(task_ids=task_ids)
        await state.set_state(Data.task_for_review)
        if not task_list:
            msg = lexicon["no_artifacts_yet"]
        await message.answer(
            msg,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_list_keyboard(
                    len(tasks_for_review), end=len(tasks_for_review))))
    except KeyError as err:
        logger.error(
            f'Ошибка в ключе при отправке списка заданий методисту: {err}')
    except Exception as err:
        logger.error(f'Ошибка при отправке списка заданий методисту: {err}')

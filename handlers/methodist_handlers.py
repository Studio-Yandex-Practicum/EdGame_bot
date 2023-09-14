import logging
import time

from aiogram import Router, F, types
from aiogram.types import (
    Message, CallbackQuery, ReplyKeyboardMarkup, InlineKeyboardMarkup,
    ReplyKeyboardRemove, InputMediaPhoto, InputMediaVideo)
from aiogram.fsm.context import FSMContext

from lexicon.lexicon import LEXICON, BUTTONS
from keyboards.counselor_keyboard import (create_yes_no_keyboard)
from keyboards.keyboards import (
    task_list_keyboard, help_keyboard, edit_profile_keyboard,
    choose_language_keyboard)
from keyboards.methodist_keyboards import (
    methodist_profile_keyboard, add_task_keyboard, task_type_keyboard,
    artifact_type_keyboard, confirm_task_keyboard, edit_task_keyboard,
    task_keyboard_methodist, review_keyboard_methodist)
from utils.db_commands import (
    get_all_achievements, select_user, create_achievement, approve_task,
    set_achievement_param, set_user_param, get_user_achievement, reject_task)
from utils.utils import (
    process_next_achievements, process_previous_achievements,
    get_achievement_info, generate_profile_info)
from utils.states_form import TaskList, AddTask, EditTask, ReviewTask, Data
from config_data.config import Pagination
from filters.custom_filters import IsMethodist

logger = logging.getLogger(__name__)

methodist_router = Router()
methodist_router.message.filter(IsMethodist())
methodist_router.callback_query.filter(IsMethodist())

ACHIEVEMENT_TYPES = ['individual', 'teamwork']
ARTIFACT_TYPES = ['text', 'image', 'video']


@methodist_router.message(F.media_group_id)
async def album_handler(message: Message, album: dict):
    try:
        media_group = [
            InputMediaPhoto(media=m.photo[-1].file_id)
            for m in album
        ]
        await message.answer_media_group(media_group)
    except Exception as err:
        print(err)


# Обработчики обычных кнопок
@methodist_router.message(F.text.in_([
    BUTTONS["RU"]["lk"],
    BUTTONS["TT"]["lk"],
    BUTTONS["EN"]["lk"]]))
async def profile_info(message: Message, state: FSMContext):
    '''Обработчик показывает главное меню профиля методиста.'''
    try:
        await state.clear()
        user = select_user(message.from_user.id)
        language = user.language
        lexicon = LEXICON[language]
        # Генерируем инфу для ЛК
        msg = generate_profile_info(user, lexicon)
        await message.answer(
            msg,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=methodist_profile_keyboard(language),
                resize_keyboard=True,
                one_time_keyboard=True))
    except KeyError as err:
        logger.error(
            f'Ошибка в ключе при открытии личного кабинета методиста: {err}')
    except Exception as err:
        logger.error(f'Ошибка при открытии личного кабинета методиста: {err}')


@methodist_router.callback_query(F.data == 'profile')
async def profile_info_callback_query(query: CallbackQuery, state: FSMContext):
    '''Обработчик показывает главное меню профиля методиста.'''
    try:
        await query.answer()
        await state.clear()
        # Достаем инфу о пользователе из базы
        user = select_user(query.from_user.id)
        language = user.language
        lexicon = LEXICON[user.language]
        # Генерируем инфу для ЛК
        msg = generate_profile_info(user, lexicon)
        await query.message.answer(
            msg,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=methodist_profile_keyboard(language),
                resize_keyboard=True,
                one_time_keyboard=True))
    except KeyError as err:
        logger.error(
            f'Ошибка в ключевом слове при открытии личного кабинета: {err}')
    except Exception as err:
        logger.error(f'Ошибка при открытии личного кабинета: {err}')


@methodist_router.message(F.text.in_([
    BUTTONS["RU"]["help"],
    BUTTONS["TT"]["help"],
    BUTTONS["EN"]["help"]]))
async def help_command(message: Message):
    try:
        user = select_user(message.from_user.id)
        language = user.language
        await message.answer(
            LEXICON[language]["help_info"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=help_keyboard(language)))
    except KeyError as err:
        logger.error(
            'Ошибка в ключевом слове при обработке команды help у методиста:'
            f' {err}')
    except Exception as err:
        logger.error(f'Ошибка при обработке команды help у методиста: {err}')


@methodist_router.message(F.text.in_([
    BUTTONS["RU"]["tasks_for_review"],
    BUTTONS["TT"]["tasks_for_review"],
    BUTTONS["EN"]["tasks_for_review"]]))
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
        await state.set_state(TaskList.tasks_for_review)
        await state.update_data(task_ids=task_ids, user_language=language)
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


@methodist_router.callback_query(F.data == 'tasks_for_review')
async def tasks_for_review_callback(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик кнопки Задания на проверку. Показывает ачивки,
    отправленные методисту на проверку в статусе "pending_methodist".
    '''
    try:
        user = select_user(query.from_user.id)
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
        await state.set_state(TaskList.tasks_for_review)
        await state.update_data(task_ids=task_ids, user_language=language)
        if not task_list:
            msg = lexicon["no_artifacts_yet"]
        await query.message.answer(
            msg,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_list_keyboard(
                    len(tasks_for_review), end=len(tasks_for_review))))
    except KeyError as err:
        logger.error(
            f'Ошибка в ключе при отправке списка заданий методисту: {err}')
    except Exception as err:
        logger.error(f'Ошибка при отправке списка заданий методисту: {err}')


@methodist_router.callback_query(TaskList.tasks_for_review)
@methodist_router.callback_query(F.data.in_(
    [str(x) for x in range(Pagination.achievements_num)]))
async def show_review_task(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик кнопок выбора отдельной ачивки на проверку.
    Получаем условный id ачивки из callback_data, достаем реальный id из
    состояние Data и получаем полную инфу об ачивке из базы данных.
    '''
    try:
        await query.answer()
        data = await state.get_data()
        language = data['user_language']
        lexicon = LEXICON[language]
        task_number = int(query.data)
        task_id = data['task_ids'][str(task_number)]
        task = get_user_achievement(task_id)
        msg = (
            f'{lexicon["review_name"]} {task.achievement.name}\n'
            f'{lexicon["review_description"]} {task.achievement.description}\n'
            f'{lexicon["review_instruction"]} {task.achievement.instruction}\n'
            f'{lexicon["review_type"]} {task.achievement.achievement_type}\n'
            f'{lexicon["review_artifact"]} {task.achievement.artifact_type}\n'
            f'{lexicon["review_user"]} {task.user.name}\n'
        )
        if task.files_id:
            media = []
            if task.achievement.artifact_type == 'image':
                for file in task.files_id:
                    media.append(InputMediaPhoto(media=file))
            else:
                for file in task.files_id:
                    media.append(InputMediaVideo(media=file))
            await query.message.answer_media_group(media=media)
        else:
            await query.message.answer(str(task.message_text))
        await state.set_state(ReviewTask.pending)
        await state.update_data(task_id=task_id, user_language=language)
        await query.message.answer(
            msg,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=review_keyboard_methodist(language)))
    except KeyError as err:
        logger.error(f'Проверь правильность ключевых слов: {err}')
    except Exception as err:
        logger.error(f'Ошибка при получении ачивки: {err}')


@methodist_router.callback_query(ReviewTask.pending)
@methodist_router.callback_query(lambda c: c.data.startswith("accept"))
async def approve_methodist_handler(query: CallbackQuery, state: FSMContext):
    try:
        await query.answer()
        data = await state.get_data()
        language = data['user_language']
        lexicon = LEXICON[language]
        task_id = data['task_id']
        if approve_task(task_id):
            await query.message.answer(
                f"Задание с ID {task_id} принято!"
            )
        else:
            await query.message.answer(
                f"Не удалось найти задание с ID {task_id}."
            )
    except Exception:
        await query.message.answer(
            "Произошла ошибка при подтверждении задания."
        )


@methodist_router.callback_query(ReviewTask.pending)
@methodist_router.callback_query(lambda c: c.data.startswith("reject"))
async def reject_methodist_handler(query: CallbackQuery, state: FSMContext):
    try:
        await query.answer()
        data = await state.get_data()
        language = data['user_language']
        lexicon = LEXICON[language]
        task_id = data['task_id']
        if reject_task(task_id):
            inline_keyboard = create_yes_no_keyboard(task_id)
            await query.message.answer(
                f"Задание с ID {task_id} отклонено! Хотите указать причину отказа?",
                reply_markup=inline_keyboard,
            )
        else:
            await query.message.answer(
                f"Не удалось найти задание с ID {task_id}."
            )
    except Exception:
        await query.message.answer(
            "Произошла ошибка при отклонении задания."
        )


@methodist_router.callback_query(F.data == "yes_handler")
@methodist_router.callback_query(lambda c: c.data.startswith("yes:"))
async def yes_methodist_handler(query: CallbackQuery, state: FSMContext):
    try:
        await query.answer()
        data = await state.get_data()
        language = data['user_language']
        lexicon = LEXICON[language]
        task_id = data['task_id']
        await state.set_state(ReviewTask.reject_message)
        await state.set_data({"task_id": task_id})
        await query.message.answer(
            "Введите причину отказа следующим сообщением. Если передумаете - введите 'Отмена'"
        )
    except Exception:
        await query.message.answer(
            "Произошла ошибка при обработке запроса."
        )


@methodist_router.message(ReviewTask.reject_message)
async def rejection_reason(message: types.Message, state: FSMContext):
    task_data = await state.get_data()
    task_id = task_data.get("task_id")

    if message.text != "Отмена":
        save_rejection_reason_in_db(session, task_id, message.text)
        await message.answer("Причина отказа сохранена")
    else:
        await message.answer(
            "Хорошо! Сообщение об отмене будет доставлено без комментария"
        )
        await state.clear()


# Обработчики добавления задания
@methodist_router.message(F.text.in_([
    BUTTONS["RU"]["add_task"],
    BUTTONS["TT"]["add_task"],
    BUTTONS["EN"]["add_task"]]))
async def add_task(message: Message):
    '''Обработчик кнопки Добавить задание.'''
    try:
        user = select_user(message.from_user.id)
        language = user.language
        lexicon = LEXICON[language]
        await message.answer(
            lexicon["add_task"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=add_task_keyboard(language)))
    except KeyError as err:
        logger.error(f'Ошибка в ключе при добавлении задания в базу: {err}')
    except Exception as err:
        logger.error(f'Ошибка при добавлении задания в базу: {err}')


@methodist_router.callback_query(F.data == 'ready')
async def start_add_task(query: CallbackQuery, state: FSMContext):
    '''Начинает сценарий добавления ачивки в базу.'''
    try:
        await query.answer()
        await state.clear()
        user = select_user(query.from_user.id)
        language = user.language
        lexicon = LEXICON[language]
        await state.update_data(user_language=language)
        await state.set_state(AddTask.name)
        await query.message.answer(lexicon["send_task_name"])
    except KeyError as err:
        logger.error(f'Ошибка в ключе при запросе названия ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе названия ачивки: {err}')


@methodist_router.message(AddTask.name)
async def process_add_task_name(message: Message, state: FSMContext):
    '''Принимает название ачивки, запрашивает описание.'''
    try:
        data = await state.get_data()
        language = data['user_language']
        await state.update_data(name=message.text)
        await state.set_state(AddTask.description)
        await message.answer(LEXICON[language]["send_task_description"])
    except KeyError as err:
        logger.error(f'Ошибка в ключе при запросе описания ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе описания ачивки: {err}')


@methodist_router.message(AddTask.description)
async def process_add_task_description(message: Message, state: FSMContext):
    '''Принимает описание ачивки, запрашивает инструкцию.'''
    try:
        data = await state.get_data()
        language = data['user_language']
        await state.update_data(description=message.text)
        await state.set_state(AddTask.instruction)
        await message.answer(LEXICON[language]["send_task_instruction"])
    except KeyError as err:
        logger.error(
            f'Ошибка в ключе при запросе инструкции для ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе инструкции для ачивки: {err}')


@methodist_router.message(AddTask.instruction)
async def process_add_task_instruction(message: Message, state: FSMContext):
    '''Принимает инструкцию ачивки, запрашивает колв-во начисляемых баллов.'''
    try:
        data = await state.get_data()
        language = data['user_language']
        await state.update_data(instruction=message.text)
        await state.set_state(AddTask.score)
        await message.answer(LEXICON[language]["send_task_score"])
    except KeyError as err:
        logger.error(f'Ошибка в ключе при запросе баллов ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе баллов ачивки: {err}')


@methodist_router.message(AddTask.score)
async def process_add_task_score(message: Message, state: FSMContext):
    '''
    Принимает кол-во начисляемых баллов за ачивку,
    запрашивает кол-во баллов для открытия ачивки.
    '''
    try:
        data = await state.get_data()
        language = data['user_language']
        lexicon = LEXICON[language]
        await state.update_data(score=int(message.text))
        await state.set_state(AddTask.price)
        await message.answer(lexicon["send_task_price"])
    except KeyError as err:
        logger.error(f'Ошибка в ключе при запросе баллов ачивки: {err}')
    except ValueError as err:
        logger.error(f'Неправильный тип данных для баллов: {err}')
        await state.set_state(AddTask.score)
        await message.answer(lexicon["ask_number_again"])
    except Exception as err:
        logger.error(f'Ошибка при запросе баллов ачивки: {err}')


@methodist_router.message(AddTask.price)
async def process_add_task_price(message: Message, state: FSMContext):
    '''Принимает кол-во баллов для открытия ачивки, запрашивает тип ачивки.'''
    try:
        data = await state.get_data()
        language = data['user_language']
        lexicon = LEXICON[language]
        await state.update_data(price=int(message.text))
        await state.set_state(AddTask.achievement_type)
        await message.answer(
            lexicon["send_task_type"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_type_keyboard(language)))
    except KeyError as err:
        logger.error(
            f'Ошибка в ключе при запросе баллов для открытия ачивки: {err}')
    except ValueError as err:
        logger.error(f'Неправильный тип данных для баллов: {err}')
        await state.set_state(AddTask.price)
        await message.answer(lexicon["ask_number_again"])
    except Exception as err:
        logger.error(f'Ошибка при запросе баллов для открытия ачивки: {err}')


@methodist_router.callback_query(AddTask.achievement_type)
async def process_add_task_type(query: CallbackQuery, state: FSMContext):
    '''Принимает тип ачивки, запрашивает тип артефакта.'''
    try:
        await query.answer()
        data = await state.get_data()
        language = data['user_language']
        await state.update_data(achievement_type=query.data)
        await state.set_state(AddTask.artifact_type)
        await query.message.edit_text(
            LEXICON[language]["send_task_artifact_type"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=artifact_type_keyboard(language)))
    except KeyError as err:
        logger.error(f'Ошибка в ключе при запросе баллов ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе баллов ачивки: {err}')


@methodist_router.callback_query(AddTask.artifact_type)
async def process_add_task_artifact_type(query: CallbackQuery,
                                         state: FSMContext):
    '''Принимает тип артефакта, запрашивает изображение для ачивки.'''
    try:
        await query.answer()
        data = await state.get_data()
        language = data['user_language']
        await state.update_data(artifact_type=query.data)
        await state.set_state(AddTask.image)
        await query.message.edit_text(LEXICON[language]["send_task_image"])
    except KeyError as err:
        logger.error(f'Ошибка в ключе при запросе баллов ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе баллов ачивки: {err}')


@methodist_router.message(AddTask.image)
async def process_add_task_image(message: Message, state: FSMContext):
    '''
    Принимает изображение для ачивки, сохраняет ачивку в БД.
    Отправляет собранные данные для подтверждения корректности
    или для перехода к редактированию.
    '''
    try:
        data = await state.get_data()
        await state.clear()
        language = data['user_language']
        lexicon = LEXICON[language]
        if not message.photo:
            await state.set_state(AddTask.image)
            await message.answer(lexicon["ask_image_again"])
        data["image"] = message.photo[0].file_id
        task_created = create_achievement(data)
        if not task_created:
            await message.answer(
                lexicon["error_adding_task"],
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=methodist_profile_keyboard(language),
                    resize_keyboard=True,
                    one_time_keyboard=True))
        task_info = get_achievement_info(data["name"], lexicon)
        info = task_info["info"]
        image = task_info["image"]
        task_id = task_info["id"]
        await state.set_state(EditTask.confirm_task)
        await state.update_data(task_id=task_id, user_language=language)
        # Сообщаем пользователю, что сейчас покажем, что получилось
        await message.answer(lexicon["confirm_adding_task"])
        time.sleep(2)
        # Показываем, что получилось
        await message.answer_photo(
            photo=image,
            caption=info,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=confirm_task_keyboard(language)))
    except KeyError as err:
        logger.error(
            f'Ошибка в ключе при запросе подтверждения ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе подтверждения ачивки: {err}')


@methodist_router.callback_query(EditTask.confirm_task, F.data == 'confirm')
async def process_saving_task_to_db(query: CallbackQuery, state: FSMContext):
    '''Обработчик кнопки Подтверждаю.'''
    try:
        await query.answer()
        data = await state.get_data()
        await state.clear()
        language = data['user_language']
        lexicon = LEXICON[language]
        await query.message.answer(
            lexicon["task_added"],
            reply_markup=ReplyKeyboardMarkup(
                keyboard=methodist_profile_keyboard(language),
                resize_keyboard=True,
                one_time_keyboard=True))
    except KeyError as err:
        logger.error(
            f'Ошибка в ключе при добавлении ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при добавлении ачивки: {err}')


# Обработчики редактирования задания
@methodist_router.message(F.text.in_([
    BUTTONS["RU"]["achievement_list"],
    BUTTONS["TT"]["achievement_list"],
    BUTTONS["EN"]["achievement_list"]]))
async def show_task_list(message: Message, state: FSMContext):
    '''
    Обарботчик кнопки Посмотреть/редактировать ачивки.
    Показывает все созданные ачивки с пагинацией.
    '''
    try:
        await state.clear()
        user = select_user(message.from_user.id)
        language = user.language
        lexicon = LEXICON[language]
        tasks = get_all_achievements()
        info = process_next_achievements(
            tasks=tasks,
            lexicon=lexicon,
            page_size=Pagination.page_size,
            methodist=True)
        msg = info["msg"]
        task_ids = info["task_ids"]
        task_info = info["task_info"]
        final_item = task_info['final_item']
        await state.set_state(TaskList.tasks)
        await state.update_data(
            tasks=task_ids, task_info=task_info, user_language=language)
        await message.answer(
            msg,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_list_keyboard(
                    len(tasks), end=final_item)))
    except KeyError as err:
        logger.error(
            f'Ошибка в ключе при просмотре списка заданий: {err}')
    except Exception as err:
        logger.error(f'Ошибка при просмотре списка заданий: {err}')


@methodist_router.callback_query(F.data == 'achievement_list')
async def show_task_list_callback(query: CallbackQuery, state: FSMContext):
    '''
    Обарботчик кнопки Посмотреть/редактировать ачивки.
    Показывает все созданные ачивки с пагинацией.
    '''
    try:
        await query.answer()
        await state.clear()
        user = select_user(query.from_user.id)
        language = user.language
        lexicon = LEXICON[language]
        tasks = get_all_achievements()
        info = process_next_achievements(
            tasks=tasks,
            lexicon=lexicon,
            page_size=Pagination.page_size,
            methodist=True)
        msg = info["msg"]
        task_ids = info["task_ids"]
        task_info = info["task_info"]
        final_item = task_info['final_item']
        await state.set_state(TaskList.tasks)
        await state.update_data(
            tasks=task_ids, task_info=task_info, user_language=language)
        await query.message.answer(
            msg,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_list_keyboard(
                    len(tasks), end=final_item)))
    except KeyError as err:
        logger.error(
            f'Ошибка в ключе при просмотре списка заданий: {err}')
    except Exception as err:
        logger.error(f'Ошибка при просмотре списка заданий: {err}')


@methodist_router.callback_query(F.data == 'next')
async def process_next_task_list(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик-пагинатор кнопки next. Достает инфу из машины
    состояний без запроса к базе.
    '''
    try:
        await query.answer()
        data = await state.get_data()
        language = data['user_language']
        lexicon = LEXICON[language]
        tasks = data['task_info']['tasks']
        count = data['task_info']['count']
        previous_final_item = data['task_info']['final_item']
        info = process_next_achievements(
            tasks=tasks,
            lexicon=lexicon,
            count=count,
            previous_final_item=previous_final_item,
            page_size=Pagination.page_size,
            methodist=True)
        msg = info["msg"]
        task_ids = info["task_ids"]
        task_info = info["task_info"]
        final_item = task_info['final_item']
        await state.update_data(tasks=task_ids, task_info=task_info)
        await state.set_state(TaskList.tasks)
        await query.message.edit_text(
                msg,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=task_list_keyboard(
                        len(tasks), previous_final_item, final_item)))
    except KeyError as err:
        logger.error(
            'Проверь правильность ключевых слов в обработке '
            f'next методиста: {err}')
    except Exception as err:
        logger.error(f'Ошибка при обработке next методиста. {err}')


@methodist_router.callback_query(F.data == 'previous')
async def process_previous_task_list(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик-пагинатор кнопки previous. Достает инфу из машины
    состояний без запроса к базе.
    '''
    try:
        await query.answer()
        data = await state.get_data()
        language = data['user_language']
        lexicon = LEXICON[language]
        tasks = data['task_info']['tasks']
        count = data['task_info']['count']
        previous_final_item = data['task_info']['final_item']
        info = process_previous_achievements(
            tasks=tasks,
            lexicon=lexicon,
            count=count,
            previous_final_item=previous_final_item,
            page_size=Pagination.page_size,
            methodist=True)
        msg = info["msg"]
        task_ids = info["task_ids"]
        task_info = info["task_info"]
        first_item = task_info['first_item']
        final_item = task_info['final_item']
        await state.update_data(tasks=task_ids, task_info=task_info)
        await state.set_state(TaskList.tasks)
        await query.message.edit_text(
                msg,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=task_list_keyboard(
                        len(tasks), first_item, final_item)))
    except KeyError as err:
        logger.error('Проверь правильность ключевых слов в обработке '
                     f'previous методиста: {err}')
    except Exception as err:
        logger.error(f'Ошибка при обработке previous методиста. {err}')


@methodist_router.callback_query(TaskList.tasks)
@methodist_router.callback_query(F.data.in_(
    [str(x) for x in range(Pagination.achievements_num)]))
async def show_task(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик кнопок выбора отдельной ачивки.
    Получаем условный id ачивки из callback_data, достаем реальный id из
    состояние Data и получаем полную инфу об ачивке из базы данных.
    '''
    try:
        await query.answer()
        data = await state.get_data()
        if not data:
            user = select_user(query.from_user.id)
            await query.message.answer(
                LEXICON[user.language]["error_getting_achievement"],
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=task_keyboard_methodist(user.language)))
            return
        language = data['user_language']
        lexicon = LEXICON[language]
        task_number = int(query.data)
        # Достаем id ачивки из состояния и делаем запрос к базе
        task_id = data['tasks'][task_number]
        # Получаем текст для сообщения и изображение ачивки
        info_image = get_achievement_info(task_id, lexicon)
        info = info_image["info"]
        image = info_image["image"]
        msg = (
            f'{lexicon["achievement_chosen"]}\n\n'
            f'{info}\n\n')
        await state.set_state(EditTask.task_id)
        await state.update_data(task_id=task_id, user_language=language)
        if not image:
            await query.message.answer(
                msg,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=task_keyboard_methodist(language)))
            return
        await query.message.answer_photo(
            photo=image,
            caption=msg,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_keyboard_methodist(language)))
    except KeyError as err:
        logger.error(f'Проверь правильность ключевых слов: {err}')
    except Exception as err:
        logger.error(f'Ошибка при получении ачивки: {err}')


# Блок редактирования ачивки
@methodist_router.callback_query(F.data == 'complete_editing')
async def process_complete_editing(query: CallbackQuery, state: FSMContext):
    '''Завершает сценарий редактирования задания.'''
    try:
        await query.answer()
        data = await state.get_data()
        await state.clear()
        language = data['user_language']
        lexicon = LEXICON[language]
        await query.message.answer(
            lexicon["editing_completed"],
            reply_markup=ReplyKeyboardMarkup(
                keyboard=methodist_profile_keyboard(language)))
    except KeyError as err:
        logger.error(
            f'Ошибка в ключе при завершении редактирования ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при завершении редактирования ачивки: {err}')


@methodist_router.callback_query(EditTask.task_id, F.data == 'edit_task')
@methodist_router.callback_query(EditTask.confirm_task, F.data == 'edit_task')
async def process_edit_task(query: CallbackQuery, state: FSMContext):
    '''
    Обарботчик инлайн кнопки Редактировать задание.
    Начинает сценарий внесения изменений в базу.
    '''
    try:
        await query.answer()
        data = await state.get_data()
        language = data['user_language']
        lexicon = LEXICON[language]
        await query.message.answer(
            lexicon["start_edit_task"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=edit_task_keyboard(language))
        )
    except KeyError as err:
        logger.error(
            f'Ошибка в ключе при начале редактирования задания: {err}')
    except Exception as err:
        logger.error(f'Ошибка при начале редактирования задания: {err}')


@methodist_router.callback_query(F.data == 'edit_name')
async def edit_name(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик создает состояние для смены названия ачивки, просит
    прислать сообщение.
    '''
    try:
        await query.answer()
        data = await state.get_data()
        await state.set_state(EditTask.name)
        language = data['user_language']
        lexicon = LEXICON[language]
        await query.message.answer(lexicon["edit_task_name"])
    except KeyError as err:
        logger.error('Ошибка в ключевом слове при запросе нового '
                     f'названия ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе нового названия ачивки: {err}')


@methodist_router.message(EditTask.name)
async def process_edit_name(message: Message, state: FSMContext):
    '''Обрабатывает сообщение для изменения названия ачивки.'''
    try:
        data = await state.get_data()
        language = data['user_language']
        lexicon = LEXICON[language]
        task_saved = set_achievement_param(
            achievement_id=data["task_id"], name=message.text)
        if not task_saved:
            await message.answer(
                lexicon["error_adding_task"],
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=methodist_profile_keyboard(language)))
            return
        # await state.update_data(name=message.text)
        await message.answer(
            lexicon["task_edited"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=edit_task_keyboard(language)))
    except KeyError as err:
        logger.error(
            f'Ошибка в ключевом слове при изменении названия ачивк: {err}')
    except Exception as err:
        logger.error(f'Ошибка при изменении названия ачивк: {err}')


@methodist_router.callback_query(F.data == 'edit_image')
async def change_image(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик создает состояние для смены изображения ачивки, просит
    прислать фото.
    '''
    try:
        await query.answer()
        data = await state.get_data()
        await state.set_state(EditTask.image)
        language = data['user_language']
        lexicon = LEXICON[language]
        await query.message.answer(lexicon["edit_task_image"])
    except KeyError as err:
        logger.error('Ошибка в ключевом слове при запросе нового '
                     f'фото ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе нового фото ачивки: {err}')


@methodist_router.message(EditTask.image)
async def process_change_image(message: Message, state: FSMContext):
    '''Обрабатывает сообщение для изменения изображения ачивки.'''
    try:
        data = await state.get_data()
        language = data['user_language']
        lexicon = LEXICON[language]
        if not message.photo:
            await state.set_state(EditTask.image)
            await message.answer(lexicon["ask_image_again"])
            return
        task_saved = set_achievement_param(
            achievement_id=data["task_id"], image=message.photo[-1].file_id)
        if not task_saved:
            await message.answer(
                lexicon["error_adding_task"],
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=methodist_profile_keyboard(language)))
            return
        # await state.update_data(image=message.photo[0].file_id)
        await message.answer(
            lexicon["task_edited"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=edit_task_keyboard(language)))
    except KeyError as err:
        logger.error(
            f'Ошибка в ключевом слове при изменении фото ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при изменении фото ачивки: {err}')


@methodist_router.callback_query(F.data == 'edit_description')
async def change_description(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик создает состояние для смены описания ачивки, просит
    прислать текст.
    '''
    try:
        await query.answer()
        data = await state.get_data()
        await state.set_state(EditTask.description)
        language = data['user_language']
        lexicon = LEXICON[language]
        await query.message.answer(lexicon["edit_task_description"])
    except KeyError as err:
        logger.error('Ошибка в ключевом слове при запросе нового '
                     f'описания ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе нового описания ачивки: {err}')


@methodist_router.message(EditTask.description)
async def process_change_description(message: Message, state: FSMContext):
    '''Обрабатывает сообщение для изменения описания ачивки.'''
    try:
        data = await state.get_data()
        language = data['user_language']
        lexicon = LEXICON[language]
        task_saved = set_achievement_param(
            achievement_id=data["task_id"], description=message.text)
        if not task_saved:
            await message.answer(
                lexicon["error_adding_task"],
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=methodist_profile_keyboard(language)))
            return
        # await state.update_data(description=message.text)
        await message.answer(
            lexicon["task_edited"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=edit_task_keyboard(language)))
    except KeyError as err:
        logger.error(
            f'Ошибка в ключевом слове при изменении описания ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при изменении описания ачивки: {err}')


@methodist_router.callback_query(F.data == 'edit_instruction')
async def change_instruction(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик создает состояние для смены инструкции ачивки, просит
    прислать текст.
    '''
    try:
        await query.answer()
        data = await state.get_data()
        await state.set_state(EditTask.instruction)
        language = data['user_language']
        lexicon = LEXICON[language]
        await query.message.answer(lexicon["edit_task_instruction"])
    except KeyError as err:
        logger.error('Ошибка в ключевом слове при запросе новоой '
                     f'инструкции ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе новой инструкции ачивки: {err}')


@methodist_router.message(EditTask.instruction)
async def process_change_instruction(message: Message, state: FSMContext):
    '''Обрабатывает сообщение для изменения инструкции ачивки.'''
    try:
        data = await state.get_data()
        language = data['user_language']
        lexicon = LEXICON[language]
        task_saved = set_achievement_param(
            achievement_id=data["task_id"], instruction=message.text)
        if not task_saved:
            await message.answer(
                lexicon["error_adding_task"],
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=methodist_profile_keyboard(language)))
            return
        # await state.update_data(instruction=message.text)
        await message.answer(
            lexicon["task_edited"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=edit_task_keyboard(language)))
    except KeyError as err:
        logger.error(
            f'Ошибка в ключевом слове при изменении инструкции ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при изменении инструкции ачивки: {err}')


@methodist_router.callback_query(F.data == 'edit_score')
async def change_score(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик создает состояние для смены баллов ачивки, просит
    прислать число.
    '''
    try:
        await query.answer()
        data = await state.get_data()
        await state.set_state(EditTask.score)
        language = data['user_language']
        lexicon = LEXICON[language]
        await query.message.answer(lexicon["edit_task_score"])
    except KeyError as err:
        logger.error('Ошибка в ключевом слове при запросе новых '
                     f'баллов ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе новых баллов ачивки: {err}')


@methodist_router.message(EditTask.score)
async def process_change_score(message: Message, state: FSMContext):
    '''Обрабатывает сообщение для изменения баллов ачивки.'''
    try:
        data = await state.get_data()
        language = data['user_language']
        lexicon = LEXICON[language]
        task_saved = set_achievement_param(
            achievement_id=data["task_id"], score=int(message.text))
        if not task_saved:
            await message.answer(
                lexicon["error_adding_task"],
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=methodist_profile_keyboard(language)))
            return
        # await state.update_data(score=int(message.text))
        await message.answer(
            lexicon["task_edited"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=edit_task_keyboard(language)))
    except KeyError as err:
        logger.error(
            f'Ошибка в ключевом слове при изменении баллов ачивки: {err}')
    except ValueError as err:
        logger.error(f'Неправильный тип данных для баллов: {err}')
        await state.set_state(EditTask.score)
        await message.answer(lexicon["ask_number_again"])
    except Exception as err:
        logger.error(f'Ошибка при изменении баллов ачивки: {err}')


@methodist_router.callback_query(F.data == 'edit_price')
async def change_price(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик создает состояние для смены стоимости ачивки, просит
    прислать число.
    '''
    try:
        await query.answer()
        data = await state.get_data()
        await state.set_state(EditTask.price)
        language = data['user_language']
        lexicon = LEXICON[language]
        await query.message.answer(lexicon["edit_task_price"])
    except KeyError as err:
        logger.error('Ошибка в ключевом слове при запросе новой '
                     f'стоимости ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе новой стоимости ачивки: {err}')


@methodist_router.message(EditTask.price)
async def process_change_price(message: Message, state: FSMContext):
    '''Обрабатывает сообщение для изменения стоимости ачивки.'''
    try:
        data = await state.get_data()
        language = data['user_language']
        lexicon = LEXICON[language]
        task_saved = set_achievement_param(
            achievement_id=data["task_id"], price=int(message.text))
        if not task_saved:
            await message.answer(
                lexicon["error_adding_task"],
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=methodist_profile_keyboard(language)))
            return
        # await state.update_data(price=int(message.text))
        await message.answer(
            lexicon["task_edited"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=edit_task_keyboard(language)))
    except KeyError as err:
        logger.error(
            f'Ошибка в ключевом слове при изменении стоимости ачивки: {err}')
    except ValueError as err:
        logger.error(f'Неправильный тип данных для стоимости: {err}')
        await state.set_state(EditTask.price)
        await message.answer(lexicon["ask_number_again"])
    except Exception as err:
        logger.error(f'Ошибка при изменении стоимости ачивки: {err}')


@methodist_router.callback_query(F.data == 'edit_task_type')
async def change_task_type(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик создает состояние для смены типа ачивки,
    предлагает выбрать из кнопок.
    '''
    try:
        await query.answer()
        data = await state.get_data()
        await state.set_state(EditTask.achievement_type)
        language = data['user_language']
        lexicon = LEXICON[language]
        await query.message.answer(
            lexicon["edit_task_type"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=task_type_keyboard(language)))
    except KeyError as err:
        logger.error('Ошибка в ключевом слове при запросе нового '
                     f'типа ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе нового типа ачивки: {err}')


@methodist_router.callback_query(EditTask.achievement_type)
async def process_change_task_type(query: CallbackQuery, state: FSMContext):
    '''Принимает тип ачивки.'''
    try:
        await query.answer()
        data = await state.get_data()
        language = data['user_language']
        lexicon = LEXICON[language]
        task_saved = set_achievement_param(
            achievement_id=data["task_id"], achievement_type=query.data)
        if not task_saved:
            await query.message.answer(
                lexicon["error_adding_task"],
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=methodist_profile_keyboard(language)))
            return
        # await state.update_data(achievement_type=query.data)
        await query.message.edit_text(
            lexicon["task_edited"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=edit_task_keyboard(language)))
    except KeyError as err:
        logger.error(f'Ошибка в ключе при обработке типа ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при обработке типа ачивки: {err}')


@methodist_router.callback_query(F.data == 'edit_artifact_type')
async def change_artifact_type(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик создает состояние для смены типа артефакта,
    предлагает выбрать из кнопок.
    '''
    try:
        await query.answer()
        data = await state.get_data()
        await state.set_state(EditTask.artifact_type)
        language = data['user_language']
        lexicon = LEXICON[language]
        await query.message.answer(
            lexicon["edit_task_artifact_type"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=artifact_type_keyboard(language)))
    except KeyError as err:
        logger.error('Ошибка в ключевом слове при запросе нового '
                     f'типа артефакт: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе нового типа артефакта: {err}')


@methodist_router.callback_query(EditTask.artifact_type)
async def process_change_artifact_type(query: CallbackQuery,
                                       state: FSMContext):
    '''Принимает тип артефакта.'''
    try:
        await query.answer()
        data = await state.get_data()
        language = data['user_language']
        lexicon = LEXICON[language]
        task_saved = set_achievement_param(
            achievement_id=data["task_id"], artifact_type=query.data)
        if not task_saved:
            await query.message.answer(
                lexicon["error_adding_task"],
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=methodist_profile_keyboard(language)))
            return
        # await state.update_data(artifact_type=query.data)
        await query.message.edit_text(
            lexicon["task_edited"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=edit_task_keyboard(language)))
    except KeyError as err:
        logger.error(f'Ошибка в ключе при изменении типа артефакта: {err}')
    except Exception as err:
        logger.error(f'Ошибка при сохранении типа артефакта: {err}')


# Обработчики редактирования профиля
@methodist_router.message(F.text.in_([
    BUTTONS["RU"]["edit_profile"],
    BUTTONS["TT"]["edit_profile"],
    BUTTONS["EN"]["edit_profile"]]))
async def edit_profile(message: Message, state: FSMContext):
    '''Обработчик для редактирования профиля методиста.'''
    try:
        await state.clear()
        user = select_user(message.chat.id)
        await message.answer(
            LEXICON[user.language]["edit_profile"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=edit_profile_keyboard(user.language)))
    except KeyError as err:
        logger.error(f'Ошибка в ключевом слове при изменении профиля: {err}')
    except Exception as err:
        logger.error(f'Ошибка при изменении профиля: {err}')


@methodist_router.callback_query(F.data == 'change_name')
async def change_name(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик создает состояние для смены имени, просит
    прислать сообщение.
    '''
    try:
        await query.answer()
        await state.set_state(Data.change_name)
        user = select_user(query.from_user.id)
        await query.message.answer(
            LEXICON[user.language]["change_name"],
            reply_markup=ReplyKeyboardRemove())
    except KeyError as err:
        logger.error(f'Ошибка в ключевом слове при запросе имени: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе имени: {err}')


@methodist_router.message(Data.change_name)
async def process_change_name(message: Message, state: FSMContext):
    '''Обрабатывает сообщение для изменения имени.'''
    try:
        user = select_user(message.chat.id)
        set_user_param(user, name=message.text)
        await state.clear()
        await message.answer(
            LEXICON[user.language]["name_changed"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=edit_profile_keyboard(user.language)))
    except KeyError as err:
        logger.error(f'Ошибка в ключевом слове при изменении имени: {err}')
    except Exception as err:
        logger.error(f'Ошибка при изменении имени: {err}')


@methodist_router.callback_query(F.data == 'change_language')
async def change_language(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик создает состояние для смены языка, уточняет,
    какой язык установить.
    '''
    try:
        await query.answer()
        await state.set_state(Data.change_language)
        user = select_user(query.from_user.id)
        await query.message.edit_text(
            LEXICON[user.language]["change_language"],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=choose_language_keyboard))
    except KeyError as err:
        logger.error(f'Ошибка в ключевом слове при запросе языка: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе языка: {err}')


@methodist_router.callback_query(Data.change_language)
async def process_change_language(query: CallbackQuery, state: FSMContext):
    '''Обработчик для изменения языка интерфейса.'''
    try:
        await query.answer()
        await state.clear()
        user = select_user(query.from_user.id)
        # Изменяем язык бота на новый
        language = query.data
        set_user_param(user, language=language)
        await query.message.answer(
            LEXICON[language]['language_changed'],
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=edit_profile_keyboard(language)))
    except KeyError as err:
        logger.error(f'Ошибка в ключевом слове при изменении языка: {err}')
    except Exception as err:
        logger.error(f'Ошибка при изменении языка: {err}')

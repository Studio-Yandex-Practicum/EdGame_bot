import logging
import time

from aiogram import Router, F
from aiogram.filters import Text
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from lexicon.lexicon import LEXICON, BUTTONS
from keyboards.methodist_keyboards import (
    add_category_keyboard, methodist_profile_keyboard,
    confirm_category_keyboard)
from utils.db_commands import (
    get_all_categories, select_user, create_category)
from utils.utils import generate_categories_list, get_category_info
from utils.states_form import AddCategory, EditCategory
from utils.pagination import PAGE_SIZE

logger = logging.getLogger(__name__)

methodist_category_router = Router()


# Обработчики добавления категории
# @methodist_category_router.message(F.text.in_([
#     BUTTONS["RU"]["add_category"],
#     BUTTONS["TT"]["add_category"],
#     BUTTONS["EN"]["add_category"]]))
@methodist_category_router.message(Text("Добавить категорию"))
async def add_category(message: Message):
    '''Обработчик кнопки Добавить категорию.'''
    try:
        user = select_user(message.from_user.id)
        language = user.language
        lexicon = LEXICON[language]
        await message.answer(
            lexicon["add_category"],
            reply_markup=add_category_keyboard(language))
    except KeyError as err:
        logger.error(f'Ошибка в ключе при добавлении задания в базу: {err}')
    except Exception as err:
        logger.error(f'Ошибка при добавлении задания в базу: {err}')


@methodist_category_router.callback_query(F.data == 'ready')
async def start_add_task(query: CallbackQuery, state: FSMContext):
    '''Начинает сценарий добавления категории в базу.'''
    try:
        await query.answer()
        await state.clear()
        user = select_user(query.from_user.id)
        language = user.language
        lexicon = LEXICON[language]
        await state.update_data(language=language)
        await state.set_state(AddCategory.name)
        await query.message.answer(lexicon["send_category_name"])
        await query.message.delete()
    except KeyError as err:
        logger.error(f'Ошибка в ключе при запросе названия категории: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе названия категории: {err}')


@methodist_category_router.message(AddCategory.name)
async def process_add_category_name(message: Message, state: FSMContext):
    '''
    Принимает имя категории, сохраняет категорию в БД.
    Отправляет собранные данные для подтверждения корректности
    или для перехода к редактированию.
    '''
    try:
        data = await state.get_data()
        await state.clear()
        language = data['language']
        lexicon = LEXICON[language]
        data["name"] = message.text
        category_created = create_category(data)
        if not category_created:
            await message.answer(
                lexicon["error_adding_category"],
                reply_markup=methodist_profile_keyboard(language))
            return
        category_info = get_category_info(data["name"], lexicon)
        info = category_info["info"]
        category_id = category_info["id"]
        # Собираем пагинацию для списка категорий, если пользователь
        # перейдет к редактированию созданной категории
        categories = get_all_categories()
        page_info = generate_categories_list(
            categories=categories,
            lexicon=lexicon,
            current_page=0,
            page_size=PAGE_SIZE)
        categories_ids = page_info["categories_ids"]
        new_current_page = page_info["current_page"]
        query_id = None
        for key in categories_ids.keys():
            if categories_ids[key] == categories_ids:
                query_id = key
        await state.set_state(EditCategory.confirm_task)
        await state.update_data(
            category_id=category_id,
            query_id=query_id,
            current_page=new_current_page,
            task_info=page_info,
            language=language)
        # Сообщаем пользователю, что сейчас покажем, что получилось
        await message.answer(lexicon["confirm_adding_category"])
        time.sleep(2)
        # Показываем, что получилось
        await message.answer(
            info,
            reply_markup=confirm_category_keyboard(language))
    except KeyError as err:
        logger.error(
            f'Ошибка в ключе при запросе подтверждения ачивки: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе подтверждения ачивки: {err}')

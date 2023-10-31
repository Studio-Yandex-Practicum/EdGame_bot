import logging
import time

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from lexicon.lexicon import LEXICON, BUTTONS
from keyboards.keyboards import pagination_keyboard
from keyboards.methodist_keyboards import (
    add_category_keyboard, edit_category_keyboard, methodist_profile_keyboard,
    category_keyboard_methodist, confirm_category_keyboard)
from utils.db_commands import (
    create_category, get_all_categories, select_user, set_category_param)
from utils.utils import generate_categories_list, get_category_info
from utils.states_form import AddCategory, EditCategory, CategoryList
from utils.pagination import PAGE_SIZE

logger = logging.getLogger(__name__)

methodist_category_router = Router()


# Обработчики добавления категории
@methodist_category_router.message(F.text.in_([
    BUTTONS["RU"]["add_category"],
    BUTTONS["TT"]["add_category"],
    BUTTONS["EN"]["add_category"]]))
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


@methodist_category_router.callback_query(F.data == 'edit_category')
async def process_edit_category(query: CallbackQuery, state: FSMContext):
    '''
    Обарботчик инлайн кнопки Редактировать категорию.
    Начинает сценарий внесения изменений в базу.
    '''
    try:
        await query.answer()
        data = await state.get_data()
        language = data['language']
        query_id = data["query_id"]
        lexicon = LEXICON[language]
        await query.message.answer(
            lexicon["start_edit_category"],
            reply_markup=edit_category_keyboard(language, cd=query_id))
        await query.message.delete()
    except KeyError as err:
        logger.error(
            f'Ошибка в ключе при начале редактирования задания: {err}')
    except Exception as err:
        logger.error(f'Ошибка при начале редактирования задания: {err}')


@methodist_category_router.callback_query(F.data == 'edit_category_name')
async def edit_category_name(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик создает состояние для смены названия категории, просит
    прислать сообщение.
    '''
    try:
        await query.answer()
        data = await state.get_data()
        await state.set_state(EditCategory.name)
        language = data['language']
        lexicon = LEXICON[language]
        await query.message.answer(lexicon["edit_category_name"])
        await query.message.delete()
    except KeyError as err:
        logger.error('Ошибка в ключевом слове при запросе нового '
                     f'названия категории: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе нового названия категории: {err}')


@methodist_category_router.message(EditCategory.name)
async def process_edit_name(message: Message, state: FSMContext):
    '''Обрабатывает сообщение для изменения названия категории.'''
    try:
        data = await state.get_data()
        language = data['language']
        query_id = data["query_id"]
        lexicon = LEXICON[language]
        category_saved = set_category_param(
            category_id=data["category_id"], name=message.text)
        if not category_saved:
            await message.answer(
                lexicon["error_adding_category"],
                reply_markup=methodist_profile_keyboard(language))
            return
        await message.answer(
            lexicon["category_edited"],
            reply_markup=edit_category_keyboard(language, cd=query_id))
    except KeyError as err:
        logger.error(
            f'Ошибка в ключевом слове при изменении названия категории: {err}')
    except Exception as err:
        logger.error(f'Ошибка при изменении названия категории: {err}')


@methodist_category_router.callback_query(
    F.data.in_({'back_to_category_list', 'category:next', 'category:previous'}))
async def show_category_list_callback(query: CallbackQuery, state: FSMContext):
    '''
    Обарботчик кнопки Посмотреть/редактировать категории.
    Показывает все созданные категории с пагинацией.
    '''
    try:
        await query.answer()
        data = await state.get_data()
        categories = data['task_info']['categories']
        current_page = data["current_page"]
        language = data['language']
        lexicon = LEXICON[language]
        if query.data == 'category:next':
            current_page += 1
        elif query.data == 'category:previous':
            current_page -= 1
        page_info = generate_categories_list(
            categories=categories,
            lexicon=lexicon,
            current_page=current_page,
            page_size=PAGE_SIZE,
            methodist=True)
        msg = page_info["msg"]
        first_item = page_info["first_item"]
        final_item = page_info["final_item"]
        new_current_page = page_info["current_page"]
        lk_button = {
            "text": BUTTONS[language]["lk"],
            "callback_data": "profile"
        }
        await state.set_state(CategoryList.categories)
        await state.update_data(
            categories=categories,
            current_page=new_current_page,
            task_info=page_info)
        if query.data == 'back_to_category_list':
            # Возвращаемся со страницы категории,
            # текст нельзя редактировать
            await query.message.answer(
                msg,
                reply_markup=pagination_keyboard(
                    buttons_count=len(categories),
                    start=first_item,
                    end=final_item,
                    cd='category',
                    page_size=PAGE_SIZE,
                    extra_button=lk_button))
            await query.message.delete()
            return
        await query.message.edit_text(
            msg,
            reply_markup=pagination_keyboard(
                buttons_count=len(categories),
                start=first_item,
                end=final_item,
                cd='category',
                page_size=PAGE_SIZE,
                extra_button=lk_button))
    except KeyError as err:
        logger.error(
            f'Ошибка в ключе при просмотре списка категорий: {err}')
    except Exception as err:
        logger.error(f'Ошибка при просмотре списка категорий: {err}')


@methodist_category_router.callback_query(
    F.data.startswith('back_to_category:') | F.data.startswith('category:'))
async def show_category(query: CallbackQuery, state: FSMContext):
    '''
    Обработчик кнопок выбора отдельной категории.
    Получаем условный id категории из callback_data, достаем реальный id из
    состояние Data и получаем полную инфу о категории из базы данных.
    '''
    try:
        await query.answer()
        data = await state.get_data()
        if not data:
            user = select_user(query.from_user.id)
            await query.message.answer(
                LEXICON[user.language]["error_getting_category"],
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=category_keyboard_methodist(user.language)))
            return
        language = data['language']
        lexicon = LEXICON[language]
        # Достаем id категории из состояния и делаем запрос к базе
        if query.data.startswith('category:'):
            category_ids = int(query.data.split(':')[-1])
            category_id = data['category_ids'][category_ids]
        elif query.data.startswith('back_to_category:'):
            category_id = data['category_id']
        # Получаем текст категории для сообщения
        category_info = get_category_info(category_id, lexicon)
        info = category_info["info"]
        msg = (
            f'{lexicon["category_chosen"]}\n\n'
            f'{info}\n\n')
        await state.set_state(EditCategory.category_id)
        await state.update_data(category_id=category_id, query_id=category_id)
        await query.message.answer(
            msg,
            reply_markup=category_keyboard_methodist(language))
        await query.message.delete()
    except KeyError as err:
        logger.error(
            f'Ошибка в ключевом слове при получении категории: {err}')
    except Exception as err:
        logger.error(f'Ошибка при получении категории: {err}')


@methodist_category_router.callback_query(
    EditCategory.confirm_task, F.data == 'confirm')
async def process_saving_category_to_db(query: CallbackQuery, state: FSMContext):
    '''Обработчик кнопки Подтверждаю.'''
    try:
        await query.answer()
        data = await state.get_data()
        await state.clear()
        language = data['language']
        lexicon = LEXICON[language]
        await query.message.answer(
            lexicon["category_added"],
            reply_markup=methodist_profile_keyboard(language))
        await query.message.delete()
    except KeyError as err:
        logger.error(
            f'Ошибка в ключе при добавлении категории: {err}')
    except Exception as err:
        logger.error(f'Ошибка при добавлении категории: {err}')


@methodist_category_router.message(F.text.in_([
    BUTTONS["RU"]["category_list"],
    BUTTONS["TT"]["category_list"],
    BUTTONS["EN"]["category_list"]]))
async def show_category_list(message: Message, state: FSMContext):
    '''
    Обарботчик кнопки Посмотреть/редактировать категории.
    Показывает все созданные категории с пагинацией.
    '''
    try:
        await state.clear()
        user = select_user(message.from_user.id)
        language = user.language
        lexicon = LEXICON[language]
        categories = get_all_categories()
        if not categories:
            await message.answer(
                lexicon["no_categories_yet"],
                reply_markup=add_category_keyboard(language))
            return
        current_page = 1
        page_info = generate_categories_list(
            categories=categories,
            lexicon=lexicon,
            current_page=current_page,
            page_size=PAGE_SIZE,
            methodist=True)
        msg = page_info["msg"]
        category_ids = page_info["categories_ids"]
        first_item = page_info["first_item"]
        final_item = page_info["final_item"]
        lk_button = {
            "text": BUTTONS[language]["lk"],
            "callback_data": "profile"
        }
        await state.set_state(CategoryList.categories)
        await state.update_data(
            categories=categories,
            category_ids=category_ids,
            current_page=current_page,
            task_info=page_info,
            language=language)
        await message.answer(
            msg,
            reply_markup=pagination_keyboard(
                buttons_count=len(categories),
                start=first_item,
                end=final_item,
                cd='category',
                page_size=PAGE_SIZE,
                extra_button=lk_button))
    except KeyError as err:
        logger.error(
            f'Ошибка в ключе при просмотре списка категорий: {err}')
    except Exception as err:
        logger.error(f'Ошибка при просмотре списка категорий: {err}')

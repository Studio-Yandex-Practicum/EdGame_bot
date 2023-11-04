import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.keyboards import pagination_keyboard
from keyboards.methodist_keyboards import (
    methodist_profile_keyboard, create_team_keyboard,
    choose_team_size_keyboard, add_members_or_pass_keyboard,
    choose_member_keyboard, delete_user_from_team_keyboard,
    team_keyboard_methodist, team_limit_reached_keyboard, edit_team_keyboard)
from utils.utils import (
    generate_profile_info, generate_users_list, generate_teams_list,
    generate_team_info)
from utils.db_commands import (
    select_user, set_user_param, create_team, set_team_param, get_all_teams,
    get_team, get_users_by_role)
from utils.pagination import PAGE_SIZE
from utils.states_form import CreateTeam, EditTeam

from lexicon.lexicon import LEXICON, BUTTONS, CD

logger = logging.getLogger(__name__)

methodist_team_router = Router()


# Создание команды
@methodist_team_router.message(F.text.in_([
    BUTTONS["RU"]["create_team"],
    BUTTONS["TT"]["create_team"],
    BUTTONS["EN"]["create_team"]]))
async def process_create_team(message: Message, state: FSMContext):
    """Обработчик кнопки создать команду."""
    try:
        user = select_user(message.from_user.id)
        language = user.language
        lexicon = LEXICON[language]
        await message.answer(
            lexicon["create_team_instruction"],
            reply_markup=create_team_keyboard(language))
        await state.set_state(CreateTeam.ready)
        await state.update_data(language=language)
    except KeyError as err:
        logger.error(
            f'Ошибка в ключевом слове при старте создания команды: {err}')
    except Exception as err:
        logger.error(f'Ошибка при старте создания команды: {err}')


@methodist_team_router.callback_query(
    CreateTeam.ready, F.data == 'ready_create_team')
async def process_ready_create_task(query: CallbackQuery, state: FSMContext):
    """Начинает процесс создания команды."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        await query.message.edit_text(lexicon["send_team_name"])
        await state.set_state(CreateTeam.name)
    except KeyError as err:
        logger.error(
            f'Ошибка в ключевом слове при запросе названия команды: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе названия команды: {err}')


@methodist_team_router.callback_query(
    CreateTeam.ready, F.data == 'cancel_create_team')
async def process_cancel_create_task(query: CallbackQuery, state: FSMContext):
    """Начинает процесс создания команды."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        await query.message.delete()
        await query.message.answer(
            lexicon["cancel_create_team"],
            reply_markup=methodist_profile_keyboard(language))
        await state.clear()
    except KeyError as err:
        logger.error(
            f'Ошибка в ключевом слове при отмене создания команды: {err}')
    except Exception as err:
        logger.error(f'Ошибка при отмене создания команды: {err}')


@methodist_team_router.message(CreateTeam.name)
async def process_team_name(message: Message, state: FSMContext):
    """Обрабатывает название команды."""
    try:
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        await state.update_data(name=message.text.title())
        await message.answer(
            lexicon["send_team_size"],
            reply_markup=choose_team_size_keyboard())
        await state.set_state(CreateTeam.size)
    except KeyError as err:
        logger.error(
            f'Ошибка в ключевом слове при запросе размера команды: {err}')
    except Exception as err:
        logger.error(f'Ошибка при запросе размера команды: {err}')


@methodist_team_router.callback_query(
    CreateTeam.size, F.data.startswith('size'))
async def process_team_size(query: CallbackQuery, state: FSMContext):
    """Обрабатывает размер команды."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        team_name = data["name"]
        team_size = int(query.data.split(':')[-1])
        new_team = create_team(name=team_name, size=team_size)
        await query.message.edit_text(
            lexicon["add_team_member"],
            reply_markup=add_members_or_pass_keyboard(language))
        await state.set_state(CreateTeam.add_members)
        await state.update_data(team=new_team)
    except KeyError as err:
        logger.error(
            'Ошибка в ключевом слове при выборе сценария '
            f'добавления членов команды: {err}')
    except Exception as err:
        logger.error(
            f'Ошибка при при выборе сценария добавления членов команды: {err}')


@methodist_team_router.callback_query(
    CreateTeam.add_members, F.data == 'pass_adding_members')
async def process_pass_adding_members(query: CallbackQuery, state: FSMContext):
    """Начинает процесс создания команды."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        await query.message.delete()
        await query.message.answer(
            lexicon["pass_adding_members"],
            reply_markup=methodist_profile_keyboard(language))
        await state.clear()
    except KeyError as err:
        logger.error(
            f'Ошибка в ключевом слове при отмене создания команды: {err}')
    except Exception as err:
        logger.error(f'Ошибка при отмене создания команды: {err}')


@methodist_team_router.callback_query(
    CreateTeam.add_members, F.data == 'add_team_members')
async def process_add_team_members(query: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки Добавить участников.
    Выводит список детей для добавления в команду.
    """
    try:
        await query.answer()
        language = select_user(query.from_user.id).language
        children = get_users_by_role(role='kid')
        current_page = 1
        pages = None
        lexicon = LEXICON[language]
        page_info = generate_users_list(
            users=children,
            lexicon=lexicon,
            current_page=current_page,
            page_size=PAGE_SIZE,
            pages=pages)
        children_ids = page_info["user_ids"]
        msg = page_info["msg"]
        first_item = page_info["first_item"]
        final_item = page_info["final_item"]
        finish_button = {
            "text": BUTTONS[language]["complete_creating_team"],
            "callback_data": "complete_creating_team"
        }
        await state.set_state(CreateTeam.choose_member)
        await state.update_data(
            pagination_info=page_info,
            children_ids=children_ids,
            children=children)
        await query.message.edit_text(
            msg,
            reply_markup=pagination_keyboard(
                len(children),
                start=first_item,
                end=final_item,
                cd='child',
                page_size=PAGE_SIZE,
                extra_button=finish_button)
        )
    except KeyError as err:
        logger.error(
            'Ошибка в ключевом слове при отображении списка детей для '
            f'добавления членов команды: {err}')
    except Exception as err:
        logger.error(
            'Ошибка при при отображении списка детей для добавления '
            f'членов команды: {err}')


@methodist_team_router.callback_query(
    F.data.in_(['child:next', 'child:previous', 'back_to_children_list']))
async def process_add_team_members_pagination(query: CallbackQuery,
                                              state: FSMContext):
    """
    Обработчик кнопки Добавить участников.
    Выводит список детей для добавления в команду.
    """
    try:
        await query.answer()
        data = await state.get_data()
        children = data["children"]
        language = data["language"]
        pagination_info = data["pagination_info"]
        current_page = pagination_info["current_page"]
        pages = pagination_info["pages"]
        if query.data == 'child:next':
            current_page += 1
        elif query.data == 'child:previous':
            current_page -= 1
        lexicon = LEXICON[language]
        page_info = generate_users_list(
            users=children,
            lexicon=lexicon,
            current_page=current_page,
            page_size=PAGE_SIZE,
            pages=pages)
        msg = page_info["msg"]
        first_item = page_info["first_item"]
        final_item = page_info["final_item"]
        finish_button = {
            "text": BUTTONS[language]["complete_creating_team"],
            "callback_data": "complete_creating_team"
        }
        await state.set_state(CreateTeam.choose_member)
        await state.update_data(pagination_info=page_info)
        await query.message.edit_text(
            msg,
            reply_markup=pagination_keyboard(
                len(children),
                start=first_item,
                end=final_item,
                cd='child',
                page_size=PAGE_SIZE,
                extra_button=finish_button)
        )
    except KeyError as err:
        logger.error(
            'Ошибка в ключевом слове при отображении списка детей для '
            f'добавления членов команды в пагинации: {err}')
    except Exception as err:
        logger.error(
            'Ошибка при при отображении списка детей для добавления '
            f'членов команды в пагинации: {err}')


@methodist_team_router.callback_query(
    CreateTeam.choose_member, F.data == 'child:info')
async def process_info_button(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(CreateTeam.choose_member)


@methodist_team_router.callback_query(
    F.data.startswith('complete_creating_team'))
async def process_complete_team(query: CallbackQuery, state: FSMContext):
    """Завершает создание команды."""
    await query.answer()
    await state.clear()
    language = select_user(query.from_user.id).language
    lexicon = LEXICON[language]
    await query.message.delete()
    await query.message.answer(
        lexicon["complete_creating_team"],
        reply_markup=methodist_profile_keyboard(language)
    )
    await state.set_state(CreateTeam.choose_member)


@methodist_team_router.callback_query(
    CreateTeam.choose_member, F.data.startswith('child'))
async def process_choose_child(query: CallbackQuery, state: FSMContext):
    """Показывает информацию о ребенке и кнопки добавления в команду."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        children_ids = data["children_ids"]
        team = data["team"]
        query_id = int(query.data.split(':')[-1])
        child_id = children_ids[query_id]
        child = select_user(child_id)
        child_info = generate_profile_info(child, lexicon)
        msg = f'{child_info}\n\n{lexicon["add_this_user"]}'
        if child.team and child.team != team:
            msg += f'\n\n{lexicon["user_already_in_other_team"]}'
        markup = (delete_user_from_team_keyboard(language)
                  if child.team == team
                  else choose_member_keyboard(language))
        if len(team.users) >= team.team_size and child.team != team:
            msg += f'\n\n{lexicon["team_limit_reached"]}'
            await query.message.edit_text(
                msg,
                reply_markup=team_limit_reached_keyboard(language)
            )
            return
        await state.update_data(child=child)
        await query.message.edit_text(
            msg,
            reply_markup=markup)
    except KeyError as err:
        logger.error(
            'Ошибка в ключевом слове при отображении информации о ребенке при '
            f'добавлении членов команды: {err}')
    except Exception as err:
        logger.error(
            'Ошибка при отображении информации о ребенке при добавлении '
            f'членов команды: {err}')


@methodist_team_router.callback_query(F.data == 'choose_member')
async def process_choose_member(query: CallbackQuery, state: FSMContext):
    try:
        await query.answer()
        data = await state.get_data()
        current_state = await state.get_state()
        language = data["language"]
        lexicon = LEXICON[language]
        child = data["child"]
        team = data["team"]
        set_user_param(child, team=team)
        child_info = generate_profile_info(child, lexicon)
        msg = f'{child_info}\n\n{lexicon["member_added"]}'
        cd = None
        if current_state == EditTeam.choose_member:
            cd = CD['edit_back_to_children_list']
        await query.message.edit_text(
            msg,
            reply_markup=delete_user_from_team_keyboard(language, cd))
    except KeyError as err:
        logger.error(
            'Ошибка в ключевом слове, когда ребенок добавлен '
            f'в команду: {err}')
    except Exception as err:
        logger.error(f'Ошибка, когда ребенок добавлен в команду: {err}')


@methodist_team_router.callback_query(F.data == 'delete_member')
async def process_delete_member(query: CallbackQuery, state: FSMContext):
    try:
        await query.answer()
        data = await state.get_data()
        current_state = await state.get_state()
        language = data["language"]
        lexicon = LEXICON[language]
        child = data["child"]
        set_user_param(child, delete_team=True)
        child_info = generate_profile_info(child, lexicon)
        msg = f'{child_info}\n\n{lexicon["member_deleted"]}'
        cd = None
        if current_state == EditTeam.choose_member:
            cd = CD['edit_back_to_children_list']
        await query.message.edit_text(
            msg,
            reply_markup=choose_member_keyboard(language, cd))
    except KeyError as err:
        logger.error(
            'Ошибка в ключевом слове, когда ребенок удален '
            f'из команды: {err}')
    except Exception as err:
        logger.error(f'Ошибка, когда ребенок удален из команды: {err}')


@methodist_team_router.message(F.text.in_([BUTTONS['RU']['team_list'],
                                           BUTTONS['TT']['team_list'],
                                           BUTTONS['EN']['team_list']]))
async def show_teams_list(message: Message, state: FSMContext):
    """Показывает список команд с возможностью выбора команды."""
    try:
        await state.clear()
        user = select_user(message.from_user.id)
        language = user.language
        lexicon = LEXICON[language]
        teams = get_all_teams()
        if not teams:
            await message.answer(
                lexicon["no_teams_yet"],
                reply_markup=create_team_keyboard(language))
            await state.set_state(CreateTeam.ready)
            await state.update_data(language=language)
            return
        current_page = 1
        page_info = generate_teams_list(
            teams=teams,
            lexicon=lexicon,
            current_page=current_page,
            page_size=PAGE_SIZE)
        msg = page_info["msg"]
        team_ids = page_info["team_ids"]
        first_item = page_info["first_item"]
        final_item = page_info["final_item"]
        lk_button = {
            "text": BUTTONS[language]["lk"],
            "callback_data": "profile"
        }
        await message.answer(
            msg,
            reply_markup=pagination_keyboard(
                buttons_count=len(teams),
                start=first_item,
                end=final_item,
                cd='team',
                page_size=PAGE_SIZE,
                extra_button=lk_button))
        await state.set_state(EditTeam.team)
        await state.update_data(
            pagination_info=page_info,
            current_page=current_page,
            team_ids=team_ids,
            teams=teams,
            language=language)
    except KeyError as err:
        logger.error(
            f'Ошибка в ключевом слове при выводе списка команд: {err}')
    except Exception as err:
        logger.error(f'Ошибка при выводе списка команд: {err}')


@methodist_team_router.callback_query(
    F.data.in_(['team:next', 'team:previous', 'back_to_team_list']))
async def process_teams_list_pagination(query: CallbackQuery,
                                        state: FSMContext):
    """Показывает список команд с возможностью выбора команды."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        teams = data["teams"]
        current_page = data["current_page"]
        if query.data == 'team:next':
            current_page += 1
        elif query.data == 'team:previous':
            current_page -= 1
        page_info = generate_teams_list(
            teams=teams,
            lexicon=lexicon,
            current_page=current_page,
            page_size=PAGE_SIZE)
        msg = page_info["msg"]
        first_item = page_info["first_item"]
        final_item = page_info["final_item"]
        new_current_page = page_info["current_page"]
        lk_button = {
            "text": BUTTONS[language]["lk"],
            "callback_data": "profile"
        }
        await query.message.edit_text(
            msg,
            reply_markup=pagination_keyboard(
                buttons_count=len(teams),
                start=first_item,
                end=final_item,
                cd='team',
                page_size=PAGE_SIZE,
                extra_button=lk_button))
        await state.set_state(EditTeam.team)
        await state.update_data(
            pagination_info=page_info,
            current_page=new_current_page,
            teams=teams)
    except KeyError as err:
        logger.error(
            'Ошибка в ключевом слове при выводе списка команд в '
            f'пагинации: {err}')
    except Exception as err:
        logger.error(f'Ошибка при выводе списка команд в пагинации: {err}')


@methodist_team_router.callback_query(
    EditTeam.team, F.data == 'team:info')
async def process_team_info_button(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(EditTeam.team)


# Редактирование команд и добавление участников
@methodist_team_router.callback_query(
    EditTeam.team, F.data.startswith('team'))
@methodist_team_router.callback_query(F.data.startswith('back_to_team'))
async def process_choose_team(query: CallbackQuery, state: FSMContext):
    """
    Показывает информацию о команде и предлагает изменить состав
    или редактировать свойства команды.
    """
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        team_ids = data["team_ids"]
        query_id = int(query.data.split(':')[-1])
        team_id = team_ids[query_id]
        team = get_team(team_id)
        team_info = generate_team_info(team, lexicon)
        msg = team_info
        await state.set_state(EditTeam.team)
        await state.update_data(team=team, query_id=query_id)
        await query.message.edit_text(
            msg,
            reply_markup=team_keyboard_methodist(language))
    except KeyError as err:
        logger.error(
            'Ошибка в ключевом слове при отображении информации о команде: '
            f'{err}')
    except Exception as err:
        logger.error(
            f'Ошибка при отображении информации о команде: {err}')


@methodist_team_router.callback_query(
    EditTeam.team, F.data == 'edit_team_members')
async def process_edit_team_members(query: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки Редактировать состав команд.
    Выводит список детей для добавления в команду.
    """
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        children = get_users_by_role(role='kid')
        current_page = 1
        lexicon = LEXICON[language]
        page_info = generate_users_list(
            users=children,
            lexicon=lexicon,
            current_page=current_page,
            page_size=PAGE_SIZE)
        children_ids = page_info["user_ids"]
        msg = page_info["msg"]
        first_item = page_info["first_item"]
        final_item = page_info["final_item"]
        back_button = {
            "text": BUTTONS[language]["back"],
            "callback_data": f"back_to_team:{data['query_id']}"
        }
        await state.set_state(EditTeam.choose_member)
        await state.update_data(
            pagination_info=page_info,
            current_page_children=current_page,
            children_ids=children_ids,
            children=children)
        await query.message.edit_text(
            msg,
            reply_markup=pagination_keyboard(
                len(children),
                start=first_item,
                end=final_item,
                cd='edit_child',
                page_size=PAGE_SIZE,
                extra_button=back_button)
        )
    except KeyError as err:
        logger.error(
            'Ошибка в ключевом слове при отображении списка детей для '
            f'при редактировании команды: {err}')
    except Exception as err:
        logger.error(
            'Ошибка при при отображении списка детей при редактировании '
            f'команды: {err}')


@methodist_team_router.callback_query(
    F.data.in_(['edit_child:next',
                'edit_child:previous',
                CD['edit_back_to_children_list']]))
async def process_edit_team_members_pagination(query: CallbackQuery,
                                               state: FSMContext):
    """
    Обработчик кнопки Добавить участников.
    Выводит список детей для добавления в команду.
    """
    try:
        await query.answer()
        data = await state.get_data()
        children = data["children"]
        language = data["language"]
        current_page = data["current_page_children"]
        if query.data == 'edit_child:next':
            current_page += 1
        elif query.data == 'edit_child:previous':
            current_page -= 1
        lexicon = LEXICON[language]
        page_info = generate_users_list(
            users=children,
            lexicon=lexicon,
            current_page=current_page,
            page_size=PAGE_SIZE)
        msg = page_info["msg"]
        first_item = page_info["first_item"]
        final_item = page_info["final_item"]
        new_current_page = page_info["current_page"]
        back_button = {
            "text": BUTTONS[language]["back"],
            "callback_data": f"back_to_team:{data['query_id']}"
        }
        await state.set_state(EditTeam.choose_member)
        await state.update_data(
            pagination_info=page_info,
            current_page_children=new_current_page)
        await query.message.edit_text(
            msg,
            reply_markup=pagination_keyboard(
                len(children),
                start=first_item,
                end=final_item,
                cd='edit_child',
                page_size=PAGE_SIZE,
                extra_button=back_button)
        )
    except KeyError as err:
        logger.error(
            'Ошибка в ключевом слове при отображении списка детей для '
            f'добавления членов команды в пагинации: {err}')
    except Exception as err:
        logger.error(
            'Ошибка при при отображении списка детей для добавления '
            f'членов команды в пагинации: {err}')


@methodist_team_router.callback_query(
    EditTeam.choose_member, F.data == 'edit_child:info')
async def process_edit_info_button(query: CallbackQuery, state: FSMContext):
    """Обработчик кнопки с номерами страниц, чтобы не зависали часики."""
    await query.answer()
    await state.set_state(EditTeam.choose_member)


@methodist_team_router.callback_query(
    EditTeam.choose_member, F.data.startswith('edit_child'))
async def process_edit_choose_child(query: CallbackQuery, state: FSMContext):
    """Показывает информацию о ребенке и кнопки добавления в команду."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        children_ids = data["children_ids"]
        team = data["team"]
        query_id = int(query.data.split(':')[-1])
        child_id = children_ids[query_id]
        child = select_user(child_id)
        child_info = generate_profile_info(child, lexicon)
        msg = f'{child_info}\n\n{lexicon["add_this_user"]}'
        cd = CD['edit_back_to_children_list']
        if child.team and child.team != team:
            msg += f'\n\n{lexicon["user_already_in_other_team"]}'
        markup = (delete_user_from_team_keyboard(language, cd)
                  if child.team == team
                  else choose_member_keyboard(language, cd))
        if len(team.users) >= team.team_size and child.team != team:
            msg += f'\n\n{lexicon["team_limit_reached"]}'
            await query.message.edit_text(
                msg,
                reply_markup=team_limit_reached_keyboard(language, cd)
            )
            return
        await state.update_data(child=child)
        await query.message.edit_text(
            msg,
            reply_markup=markup)
    except KeyError as err:
        logger.error(
            'Ошибка в ключевом слове при отображении информации о ребенке при '
            f'редактировании членов команды: {err}')
    except Exception as err:
        logger.error(
            'Ошибка при отображении информации о ребенке при редактировании '
            f'членов команды: {err}')


@methodist_team_router.callback_query(
    EditTeam.team, F.data == 'edit_team')
async def process_edit_team(query: CallbackQuery, state: FSMContext):
    """Старт сценария редактирования свойств команды."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        query_id = data["query_id"]
        lexicon = LEXICON[language]
        await query.message.edit_text(
            lexicon["start_edit_team"],
            reply_markup=edit_team_keyboard(language, cd=query_id))
        await state.set_state(EditTeam.team)
    except KeyError as err:
        logger.error(
            'Ошибка в ключевом слове при старте редактирования свойств '
            f'команды: {err}')
    except Exception as err:
        logger.error(
            f'Ошибка при старте редактирования свойств команды: {err}')


@methodist_team_router.callback_query(
    EditTeam.team, F.data == 'edit_team_name')
async def process_edit_team_name(query: CallbackQuery, state: FSMContext):
    """Запрашивает новое название команды."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        await query.message.edit_text(lexicon["edit_team_name"])
        await state.set_state(EditTeam.name)
    except KeyError as err:
        logger.error(
            'Ошибка в ключевом слове при запросе нового названия '
            f'команды: {err}')
    except Exception as err:
        logger.error(
            f'Ошибка при запросе нового названия команды: {err}')


@methodist_team_router.message(EditTeam.name)
async def process_new_team_name(message: Message, state: FSMContext):
    """Обрабатывает новое название команды."""
    try:
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        query_id = data["query_id"]
        team = data["team"]
        new_name = message.text
        set_team_param(team=team, name=new_name)
        await message.answer(
            lexicon["team_edited"],
            reply_markup=edit_team_keyboard(language, cd=query_id))
        await state.set_state(EditTeam.team)
    except KeyError as err:
        logger.error(
            'Ошибка в ключевом слове при обработке нового названия '
            f'команды: {err}')
    except Exception as err:
        logger.error(
            f'Ошибка при обработке нового названия команды: {err}')


@methodist_team_router.callback_query(
    EditTeam.team, F.data == 'edit_team_size')
async def process_edit_team_size(query: CallbackQuery, state: FSMContext):
    """Запрашивает новое название команды."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        await query.message.edit_text(
            lexicon["edit_team_size"],
            reply_markup=choose_team_size_keyboard())
        await state.set_state(EditTeam.size)
    except KeyError as err:
        logger.error(
            'Ошибка в ключевом слове при запросе нового размера '
            f'команды: {err}')
    except Exception as err:
        logger.error(
            f'Ошибка при запросе нового размера команды: {err}')


@methodist_team_router.callback_query(
    EditTeam.size, F.data.startswith('size:'))
async def process_new_team_size(query: CallbackQuery, state: FSMContext):
    """Запрашивает новое название команды."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        query_id = data["query_id"]
        team = data["team"]
        lexicon = LEXICON[language]
        new_size = int(query.data.split(':')[-1])
        set_team_param(team=team, size=new_size)
        await query.message.edit_text(
            lexicon["team_edited"],
            reply_markup=edit_team_keyboard(language, cd=query_id))
        await state.set_state(EditTeam.team)
    except KeyError as err:
        logger.error(
            'Ошибка в ключевом слове при обработке нового размера '
            f'команды: {err}')
    except Exception as err:
        logger.error(
            f'Ошибка при обработке нового размера команды: {err}')

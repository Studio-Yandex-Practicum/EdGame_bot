import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.keyboards import (
    become_cap_or_leave_team_keyboard,
    join_team_keyboard,
    leave_captain_position_keyboard,
    pagination_keyboard,
    profile_keyboard,
    team_full_keyboard,
)
from lexicon.lexicon import BUTTONS, LEXICON
from utils.db_commands import (
    get_all_teams,
    get_team,
    select_user,
    set_user_param,
)
from utils.pagination import PAGE_SIZE
from utils.states_form import JoinTeam
from utils.utils import generate_team_info, generate_teams_list

logger = logging.getLogger(__name__)

child_team_router = Router()


@child_team_router.message(
    F.text.in_(
        [
            BUTTONS["RU"]["join_team"],
            BUTTONS["TT"]["join_team"],
            BUTTONS["EN"]["join_team"],
        ]
    )
)
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
                reply_markup=profile_keyboard(language),
            )
            return
        current_page = 1
        page_info = generate_teams_list(
            teams=teams,
            lexicon=lexicon,
            current_page=current_page,
            page_size=PAGE_SIZE,
        )
        msg = page_info["msg"]
        team_ids = page_info["team_ids"]
        first_item = page_info["first_item"]
        final_item = page_info["final_item"]
        lk_button = {
            "text": BUTTONS[language]["lk"],
            "callback_data": "profile",
        }
        await message.answer(
            msg,
            reply_markup=pagination_keyboard(
                buttons_count=len(teams),
                start=first_item,
                end=final_item,
                cd="team",
                page_size=PAGE_SIZE,
                extra_button=lk_button,
            ),
        )
        await state.set_state(JoinTeam.team_chosen)
        await state.update_data(
            pagination_info=page_info,
            team_ids=team_ids,
            teams=teams,
            language=language,
            child=user,
        )
    except KeyError as err:
        logger.error(
            "Ошибка в ключевом слове при выводе списка команд для ребенка: "
            f"{err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при выводе списка команд для ребенка: {err}")


@child_team_router.callback_query(
    F.data.in_(["team:next", "team:previous", "back_to_team_list"])
)
async def process_teams_list_pagination(
    query: CallbackQuery, state: FSMContext
):
    """Показывает список команд с возможностью выбора команды."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        teams = data["teams"]
        pagination_info = data["pagination_info"]
        current_page = pagination_info["current_page"]
        if query.data == "team:next":
            current_page += 1
        elif query.data == "team:previous":
            current_page -= 1
        page_info = generate_teams_list(
            teams=teams,
            lexicon=lexicon,
            current_page=current_page,
            page_size=PAGE_SIZE,
        )
        msg = page_info["msg"]
        first_item = page_info["first_item"]
        final_item = page_info["final_item"]
        lk_button = {
            "text": BUTTONS[language]["lk"],
            "callback_data": "profile",
        }
        await query.message.edit_text(
            msg,
            reply_markup=pagination_keyboard(
                buttons_count=len(teams),
                start=first_item,
                end=final_item,
                cd="team",
                page_size=PAGE_SIZE,
                extra_button=lk_button,
            ),
        )
        await state.set_state(JoinTeam.team_chosen)
        await state.update_data(pagination_info=page_info, teams=teams)
    except KeyError as err:
        logger.error(
            "Ошибка в ключевом слове при выводе списка команд в "
            f"пагинации: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при выводе списка команд в пагинации: {err}")


@child_team_router.callback_query(JoinTeam.team_chosen, F.data == "team:info")
async def process_team_info_button(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(JoinTeam.team_chosen)


@child_team_router.callback_query(
    JoinTeam.team_chosen, F.data.startswith("team")
)
# @child_team_router.callback_query(F.data.startswith('back_to_team'))
async def process_choose_team(query: CallbackQuery, state: FSMContext):
    """
    Показывает информацию о команде и предлагает присоединиться к ней.
    """
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        child = data["child"]
        team_ids = data["team_ids"]
        query_id = int(query.data.split(":")[-1])
        team_id = team_ids[query_id]
        team = get_team(team_id)
        team_info = generate_team_info(team, lexicon)
        msg = team_info
        await state.update_data(team=team, query_id=query_id)
        if child.team and child.team != team:
            msg = f'{team_info}\n\n{lexicon["you_already_in_other_team"]}'
        elif child.team and child.team == team:
            msg = f'{team_info}\n\n{lexicon["you_in_this_team"]}'
            cap_pos_available = False
            if not team.captain:
                msg = (
                    f"{team_info}\n\n"
                    f'{lexicon["you_in_this_team"]}\n\n'
                    f'{lexicon["become_captain_instruction"]}\n\n'
                    f'{lexicon["leave_team_instruction"]}'
                )
                cap_pos_available = True
            markup = become_cap_or_leave_team_keyboard(
                language, cap_pos_available
            )
            if team.captain == child:
                msg = (
                    f"{team_info}\n\n"
                    f'{lexicon["leave_captain_position"]}\n\n'
                    f'{lexicon["leave_team_instruction"]}'
                )
                markup = leave_captain_position_keyboard(language)
            await query.message.edit_text(msg, reply_markup=markup)
            return
        if len(team.users) >= team.team_size:
            msg = f'{team_info}\n\n{lexicon["team_limit_reached_child"]}'
            await query.message.edit_text(
                msg, reply_markup=team_full_keyboard(language)
            )
            return
        await state.set_state(JoinTeam.join_team)
        await query.message.edit_text(
            msg, reply_markup=join_team_keyboard(language)
        )
    except KeyError as err:
        logger.error(
            "Ошибка в ключевом слове при отображении информации о команде "
            f"для ребенка: {err}"
        )
    except Exception as err:
        logger.error(
            f"Ошибка при отображении информации о команде для ребенка: {err}"
        )


@child_team_router.callback_query(JoinTeam.join_team, F.data == "join_team")
@child_team_router.callback_query(F.data == "join_team")
async def process_join_team(query: CallbackQuery, state: FSMContext):
    """Обрабатывает кнопку Присоединиться к команде."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        team = data["team"]
        set_user_param(data["child"], team=team, leave_captain_pos=True)
        team_info = generate_team_info(team, lexicon)
        msg = f'{team_info}\n\n{lexicon["leave_team_instruction"]}'
        cap_pos_available = False
        if not team.captain:
            msg = (
                f"{team_info}\n\n"
                f'{lexicon["become_captain_instruction"]}\n\n'
                f'{lexicon["leave_team_instruction"]}'
            )
            cap_pos_available = True
            await state.set_state(JoinTeam.become_captain)
        await query.message.edit_text(
            msg,
            reply_markup=become_cap_or_leave_team_keyboard(
                language, cap_pos_available
            ),
        )
    except KeyError as err:
        logger.error(
            f"Ошибка в ключевом слове при присоединении к команде: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при присоединении к команде: {err}")


@child_team_router.callback_query(
    JoinTeam.become_captain, F.data == "become_captain"
)
@child_team_router.callback_query(F.data == "become_captain")
async def process_become_captain(query: CallbackQuery, state: FSMContext):
    """Обрабатывает кнопку Стать капитаном."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        team = data["team"]
        set_user_param(data["child"], captain_of_team=team.id)
        team_info = generate_team_info(team, lexicon)
        msg = (
            f"{team_info}\n\n"
            f'{lexicon["leave_captain_position"]}\n\n'
            f'{lexicon["leave_team_instruction"]}'
        )
        await query.message.edit_text(
            msg, reply_markup=leave_captain_position_keyboard(language)
        )
    except KeyError as err:
        logger.error(
            f"Ошибка в ключевом слове при выборе стать капитаном: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при выборе стать капитаном: {err}")


@child_team_router.callback_query(F.data == "leave_captain_position")
async def process_leave_captain_position(
    query: CallbackQuery, state: FSMContext
):
    """Обрабатывает кнопку Уйти с позиции капитана."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        team = data["team"]
        set_user_param(data["child"], leave_captain_pos=True)
        team_info = generate_team_info(team, lexicon)
        msg = (
            f"{team_info}\n\n"
            f'{lexicon["you_left_captain_position"]}\n\n'
            f'{lexicon["leave_team_instruction"]}'
        )
        await query.message.edit_text(
            msg, reply_markup=become_cap_or_leave_team_keyboard(language)
        )
    except KeyError as err:
        logger.error(
            f"Ошибка в ключевом слове при уходе с позиции капитана: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при уходе с позиции капитана: {err}")


@child_team_router.callback_query(F.data == "leave_team")
async def process_leave_team(query: CallbackQuery, state: FSMContext):
    """Обрабатывает кнопку Уйти из команды."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        team = data["team"]
        set_user_param(data["child"], delete_team=True)
        team_info = generate_team_info(team, lexicon)
        msg = f"{team_info}\n\n" f'{lexicon["you_left_team"]}'
        await query.message.edit_text(
            msg, reply_markup=join_team_keyboard(language)
        )
    except KeyError as err:
        logger.error(
            f"Ошибка в ключевом слове при уходе с позиции капитана: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при уходе с позиции капитана: {err}")

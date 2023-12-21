import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from sqlalchemy.orm import Session

from db.models import AchievementStatus, User
from filters.custom_filters import IsCounselour
from keyboards.counsellor_keyboard import (
    create_inline_keyboard,
    create_profile_keyboard,
    create_yes_no_keyboard,
)
from lexicon.lexicon import BUTTONS, LEXICON
from utils.db_commands import (
    approve_task,
    available_achievements,
    reject_task,
    select_user,
    send_to_methdist,
)
from utils.states_form import TaskState
from utils.user_utils import (
    get_achievement_description,
    get_achievement_file_id,
    get_achievement_file_type,
    get_achievement_instruction,
    get_achievement_name,
    get_achievement_status_by_id,
    get_achievements_by_name,
    get_all_child_achievements,
    get_all_children,
    get_all_children_from_group,
    get_all_group,
    get_child_by_name_and_group,
    get_message_text,
    get_user_name,
    save_rejection_reason_in_db,
    send_task,
)

logger = logging.getLogger(__name__)

router = Router()
router.message.filter(IsCounselour())
router.callback_query.filter(IsCounselour())


@router.message(
    F.text.in_([BUTTONS["RU"]["lk"], BUTTONS["TT"]["lk"], BUTTONS["EN"]["lk"]])
)
async def enter_profile(message: types.Message, session: Session):
    user = select_user(session, message.chat.id)
    keyboard = create_profile_keyboard(user.language)
    await message.answer(
        LEXICON[user.language]["in_lk"],
        reply_markup=keyboard
    )


@router.message(
    F.text.in_([
        BUTTONS["RU"]["list_children"],
        BUTTONS["TT"]["list_children"],
        BUTTONS["EN"]["list_children"]
    ])
)
async def show_children_list(message: types.Message, session: Session):
    user = select_user(session, message.chat.id)
    try:
        children = get_all_children(session)
        children_text = "\n".join(
            [
                (
                    f"{LEXICON[user.language]['name']}: {child.name} - "
                    f"{LEXICON[user.language]['scores']}: {child.score}"
                ) for child in children
            ]
        )
        await message.answer(
            f"{LEXICON[user.language]['list_children']}:\n{children_text}"
        )
    except Exception as err:
        await message.answer(LEXICON[user.language]["list_children_err"])
        logger.error(f"Произошла ошибка при получении списка детей : {err}")


@router.message(
    F.text.in_([
        BUTTONS["RU"]["tasks_for_review"],
        BUTTONS["TT"]["tasks_for_review"],
        BUTTONS["EN"]["tasks_for_review"]
    ])
)
async def check_requests(message: types.Message, session: Session):
    user = select_user(session, message.chat.id)
    lexicon = LEXICON[user.language]
    children = session.query(User).filter(User.role == "kid").all()
    try:
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
                name = get_achievement_name(session, task.achievement_id)
                description = get_achievement_description(
                    session, task.achievement_id
                )
                instruction = get_achievement_instruction(
                    session, task.achievement_id
                )

                file_id = get_achievement_file_id(session, task.achievement_id)
                file_type = get_achievement_file_type(
                    session, task.achievement_id
                )
                message_text = get_message_text(session, task.id)
                inline_keyboard = create_inline_keyboard(
                    task.id,
                    child.name,
                    user.language
                )

                caption = (
                    f"{lexicon['task_review']} {child.name}\n\n"
                    f"{lexicon['name_task']} {name}\n\n"
                    f"{lexicon['description_task']} {description}\n\n"
                    f"{lexicon['instruction']} {instruction}"
                )
                await send_task(
                    message,
                    file_type,
                    file_id,
                    caption,
                    message_text,
                    inline_keyboard,
                )
    except Exception as err:
        await message.answer(lexicon["find_task_err"])
        logger.error(f"Произошла ошибка при поиске заданий : {err}")


@router.callback_query(lambda c: c.data.startswith("accept:"))
async def approve_handler(
    callback_query: types.CallbackQuery, session: Session
):
    user = select_user(session, callback_query.from_user.id)
    lexicon = LEXICON[user.language]
    task_id = int(callback_query.data.split(":")[1])
    name = str(callback_query.data.split(":")[2])
    try:
        if approve_task(session, task_id):
            await callback_query.message.answer(
                f"{lexicon['task_from']} {name} {lexicon['accept']}!"
            )
        else:
            await callback_query.message.answer(
                f"{lexicon['not_found_task']} {task_id}."
            )
    except Exception as err:
        await callback_query.message.answer(lexicon['err_accept_task'])
        logger.error(f"Произошла ошибка при подтверждении задания : {err}")


@router.callback_query(lambda c: c.data.startswith("reject:"))
async def reject_handler(
    callback_query: types.CallbackQuery, session: Session
):
    user = select_user(session, callback_query.from_user.id)
    lexicon = LEXICON[user.language]
    task_id = int(callback_query.data.split(":")[1])
    name = str(callback_query.data.split(":")[2])
    try:
        user = select_user(session, callback_query.from_user.id)
        if reject_task(session, task_id):
            inline_keyboard = create_yes_no_keyboard(task_id, user.language)
            await callback_query.message.answer(
                f"{lexicon['task_from']} {name} {lexicon['rejection_reason']}",
                reply_markup=inline_keyboard,
            )
        else:
            await callback_query.message.answer(
                f"{lexicon['not_found_task']} {task_id}."
            )
    except Exception as err:
        await callback_query.message.answer(lexicon['err_reject_task'])
        logger.error(f"Произошла ошибка при отклонении задания : {err}")


@router.callback_query(F.data == "yes_handler")
@router.callback_query(lambda c: c.data.startswith("yes:"))
async def yes_handler(
    callback_query: types.CallbackQuery, state: FSMContext, session: Session
):
    user = select_user(session, callback_query.from_user.id)
    lexicon = LEXICON[user.language]
    task_id = int(callback_query.data.split(":")[1])
    try:
        await state.set_state(TaskState.reject_message)
        await state.set_data({"task_id": task_id})
        await callback_query.message.answer(lexicon["message_reject"])
    except Exception as err:
        await callback_query.message.answer(lexicon["request_err"])
        logger.error(f"Произошла ошибка при обработке запроса : {err}")


@router.callback_query(F.data == "no_handler")
@router.callback_query(lambda c: c.data.startswith("no:"))
async def no_handler(callback_query: types.CallbackQuery, session: Session):
    user = select_user(session, callback_query.from_user.id)
    lexicon = LEXICON[user.language]
    try:
        await callback_query.message.answer(lexicon["no_comment"])
    except Exception as err:
        await callback_query.message.answer(lexicon["request_err"])
        logger.error(f"Произошла ошибка при обработке запроса : {err}")


@router.message(TaskState.reject_message)
async def rejection_reason(
    message: types.Message, state: FSMContext, session: Session
):
    user = select_user(session, message.chat.id)
    lexicon = LEXICON[user.language]
    task_data = await state.get_data()
    task_id = task_data.get("task_id")

    if message.text.lower() in [
        lexicon["answer_cancel"], lexicon["answer_no"]
    ]:
        await message.answer(lexicon["without_comment"])
        await state.clear()
        return
    save_rejection_reason_in_db(session, task_id, message.text)
    await message.answer(lexicon["reason_rejection"])
    await state.clear()


@router.callback_query(lambda c: c.data.startswith("back:"))
async def send_to_methodist(
    callback_query: types.CallbackQuery, session: Session
):
    user = select_user(session, callback_query.from_user.id)
    lexicon = LEXICON[user.language]
    task_id = int(callback_query.data.split(":")[1])
    name = str(callback_query.data.split(":")[2])
    if send_to_methdist(session, task_id):
        await callback_query.message.answer(
            f"Задание от {name} отправлено на проверку методисту"
        )


@router.message(
    F.text.in_([
        BUTTONS["RU"]["check_specific_task"],
        BUTTONS["TT"]["check_specific_task"],
        BUTTONS["EN"]["check_specific_task"]
    ])
)
async def display_task_review_requests(
    message: types.Message, state: FSMContext, session: Session
):
    """Отображение всех входящих заявок на проверку одного задания."""
    user = select_user(session, message.chat.id)
    lexicon = LEXICON[user.language]
    await state.set_state(TaskState.achievement_name)
    await message.answer(lexicon["name_specific_task"])


@router.message(TaskState.achievement_name)
async def display_task(
    message: types.Message, state: FSMContext, session: Session
):
    user = select_user(session, message.chat.id)
    lexicon = LEXICON[user.language]
    achievement_name = message.text
    try:
        achievement_id = get_achievements_by_name(session, achievement_name)
        name = get_achievement_name(session, achievement_id)
        description = get_achievement_description(session, achievement_id)
        instruction = get_achievement_instruction(session, achievement_id)
        file_type = get_achievement_file_type(session, achievement_id)
        await message.answer(
            f"{lexicon['name_task']} {name}\n\n"
            f"{lexicon['description_task']} {description}\n\n"
            f"{lexicon['instruction_for_task']} {instruction}"
        )
        achievements = get_achievement_status_by_id(session, achievement_id)
        for achievement in achievements:
            user_id = achievement.user_id
            file_id = get_achievement_file_id(
                session, achievement.achievement_id
            )
            message_text = achievement.message_text
            child = get_user_name(session, user_id)
            caption = f"{lexicon['task_from_child']} {child}\n\n"
            inline_keyboard = create_inline_keyboard(
                achievement.id,
                child,
                user.language
            )
            await send_task(
                message,
                file_type,
                file_id,
                caption,
                message_text,
                inline_keyboard,
            )
            await state.clear()
    except Exception as err:
        await message.answer(lexicon["err_found_task"])
        await state.clear()
        logger.error(f"Произошла ошибка при поиске задания : {err}")


@router.message(
    F.text.in_([
        BUTTONS["RU"]["squad_progress"],
        BUTTONS["TT"]["squad_progress"],
        BUTTONS["EN"]["squad_progress"]
    ])
)
async def display_troop_progress(
    message: types.Message, state: FSMContext, session: Session
):
    """Возможность отображения общего прогресса отряда."""
    user = select_user(session, message.chat.id)
    lexicon = LEXICON[user.language]
    await state.set_state(TaskState.children_group)
    await message.answer(lexicon["squad_number"])


@router.message(TaskState.children_group)
async def display_troop(
    message: types.Message, state: FSMContext, session: Session
):
    user = select_user(session, message.chat.id)
    lexicon = LEXICON[user.language]
    try:
        children = get_all_children_from_group(session, message.text)
        message_text = (
            f"{lexicon['squad_size']} {message.text} "
            f"{lexicon['amounts']} {len(children)} {lexicon['childs']}.\n\n"
        )
        score = sum(child.score for child in children)
        message_text += (
            f"{lexicon['progress_squad']} - {score} {lexicon['points']}.\n"
            f"{lexicon['personal_progress']}"
        )
        children_info_list = [
            (
                f"{lexicon['name']}: {child.name} - {lexicon['scores']}: "
                f"{child.score}"
            ) for child in children
        ]
        message_text += "\n\n".join(children_info_list)
        if len(children) != 0:
            await message.answer(message_text)
            await state.clear()
        else:
            raise Exception
    except Exception as err:
        await message.answer(lexicon["error_group"])
        await state.clear()
        logger.error(f"Произошла ошибка при поиске отряда : {err}")


@router.message(
    F.text.in_([
        BUTTONS["RU"]["child_information"],
        BUTTONS["TT"]["child_information"],
        BUTTONS["EN"]["child_information"]
    ])
)
async def check_child_info(
    message: types.Message, state: FSMContext, session: Session
):
    """Возможность проверки инфы о выбранном ребенке."""
    user = select_user(session, message.chat.id)
    lexicon = LEXICON[user.language]
    await state.set_state(TaskState.child_info)
    await message.answer(lexicon["enter_child_name"])


@router.message(TaskState.child_info)
async def check_child(
    message: types.Message, state: FSMContext, session: Session
):
    user = select_user(session, message.chat.id)
    lexicon = LEXICON[user.language]
    try:
        search_child = message.text.split(" ")
        name = f"{search_child[0]} {search_child[1]}"
        group = int(search_child[2])
        child = get_child_by_name_and_group(session, name, group)
        achievements = available_achievements(session, child.id, child.score)

        message_text = [
            f"{lexicon['child_name_info']} {name}:\n\n"
            f"{lexicon['scores']}: {child.score} {lexicon['group']}: "
            f"{child.group}, {lexicon['achievements_available']}\n",
        ]
        message_text.extend(
            f"{lexicon['task_name']}: {achievement.name}\n"
            f"{lexicon['points_required']}: {achievement.price}\n"
            f"{lexicon['type']}: {achievement.achievement_type}\n"
            f"{lexicon['points_achievement']}: {achievement.score}\n\n"
            for achievement in achievements
        )
        await message.answer("\n".join(message_text))
        await state.clear()
    except Exception as err:
        await message.answer(lexicon["error_child"])
        await state.clear()
        logger.error(f"Произошла ошибка при поиске ребенка : {err}")


@router.message(
    F.text.in_([
        BUTTONS["RU"]["check_task_specific_child"],
        BUTTONS["TT"]["check_task_specific_child"],
        BUTTONS["EN"]["check_task_specific_child"]
    ])
)
async def display_child_task_review_requests(
    message: types.Message, state: FSMContext, session: Session
):
    """Отображение всех входящих заявок на проверку заданий одного ребёнка."""
    user = select_user(session, message.chat.id)
    lexicon = LEXICON[user.language]
    await state.set_state(TaskState.child_name)
    await message.answer(lexicon["check_tasks_child"])


@router.message(TaskState.child_name)
async def display_child_task_review(
    message: types.Message, state: FSMContext, session: Session
):
    user = select_user(session, message.chat.id)
    lexicon = LEXICON[user.language]
    search_child = message.text.split(" ")
    try:
        name = f"{search_child[0]} {search_child[1]}"
        group = int(search_child[2])
        child_id = get_child_by_name_and_group(session, name, group).id
        achievements = get_all_child_achievements(session, child_id)
        if len(achievements) == 0:
            await message.answer(lexicon["no_tasks_child"])

        for achievement in achievements:
            ac_id = achievement.achievement_id
            file_id = get_achievement_file_id(session, ac_id)
            message_text = achievement.message_text
            ac_name = get_achievement_name(session, ac_id)
            description = get_achievement_description(session, ac_id)
            instruction = get_achievement_instruction(session, ac_id)
            file_type = get_achievement_file_type(session, ac_id)
            inline_keyboard = create_inline_keyboard(
                achievement.id,
                name,
                user.language
            )
            caption = (
                f"{lexicon['name_task']} {ac_name}\n\n"
                f"{lexicon['description_task']} {description}\n\n"
                f"{lexicon['instruction']} {instruction}"
            )
            await send_task(
                message,
                file_type,
                file_id,
                caption,
                message_text,
                inline_keyboard,
            )
            await state.clear()
    except Exception as err:
        await message.answer(lexicon["err_child_found"])
        await state.clear()
        logger.error(f"Произошла ошибка при поиске ребенка : {err}")


@router.message(
    F.text.in_([
        BUTTONS["RU"]["check_tasks_squad"],
        BUTTONS["TT"]["check_tasks_squad"],
        BUTTONS["EN"]["check_tasks_squad"]
    ])
)
async def display_troop_task_review_requests(
    message: types.Message, state: FSMContext, session: Session
):
    """Отображение всех входящих заявок на проверку заданий всего отряда."""
    user = select_user(session, message.chat.id)
    lexicon = LEXICON[user.language]
    await state.set_state(TaskState.group)
    await message.answer(lexicon["all_tasks_squad"])


@router.message(TaskState.group)
async def display_troop_task_review(
    message: types.Message, state: FSMContext, session: Session
):
    user = select_user(session, message.chat.id)
    lexicon = LEXICON[user.language]
    try:
        user_ids = get_all_children_from_group(session, message.text)
        if len(user_ids) == 0:
            await message.answer(lexicon["no_this_squad"])
        for child in user_ids:
            child_id = child.id
            achievements = get_all_child_achievements(session, child_id)
            child_name = get_user_name(session, child_id)
            for achievement in achievements:
                ac_id = achievement.achievement_id
                file_id = achievement.files_id
                message_text = achievement.message_text
                name = get_achievement_name(session, ac_id)
                description = get_achievement_description(session, ac_id)
                instruction = get_achievement_instruction(session, ac_id)
                file_type = get_achievement_file_type(session, ac_id)
                inline_keyboard = create_inline_keyboard(
                    achievement.id,
                    child_name,
                    user.language
                )
                caption = (
                    f"{lexicon['task_review']} {child_name}\n\n"
                    f"{lexicon['name_task']} {name}\n\n"
                    f"{lexicon['description_task']} {description}\n\n"
                    f"{lexicon['instruction']} {instruction}"
                )
                await send_task(
                    message,
                    file_type,
                    file_id,
                    caption,
                    message_text,
                    inline_keyboard,
                )
                await state.clear()
    except Exception as err:
        await message.answer(lexicon["error_group"])
        await state.clear()
        logger.error(f"Произошла ошибка при поиске отряда : {err}")


@router.message(
    F.text.in_([
        BUTTONS["RU"]["list_children_in_group"],
        BUTTONS["TT"]["list_children_in_group"],
        BUTTONS["EN"]["list_children_in_group"]
    ])
)
async def get_group_children(
    message: types.Message, state: FSMContext, session: Session
):
    """Возможность выбора группы, в которой есть ребенок."""
    try:
        user = select_user(session, message.from_user.id)
        language = user.language
        lexicon = LEXICON[language]
        teams = get_all_group(session)
        if not teams:
            await message.answer(lexicon["no_group"])
            return
        buttons = []
        for team in teams:
            button = InlineKeyboardButton(
                text=team.group, callback_data=f"{team.group},{language}"
            )
            buttons.append([button])
        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await state.set_state(TaskState.group_buttons)

        await message.answer(
            lexicon["group_number"], reply_markup=reply_markup
        )
    except Exception as err:
        await message.answer(lexicon["error_group"])
        logger.error(f"Произошла ошибка при поиске группы: {err}")
        await state.clear()


@router.callback_query(TaskState.group_buttons)
async def show_children_group(
    query: CallbackQuery, state: FSMContext, session: Session
):
    """Возможность выбора информации о ребенке."""
    try:
        await query.answer()
        await state.clear()
        td = query.data.split(",")
        group_id = int(td[0])
        language = td[1]
        lexicon = LEXICON[language]
        user_ids = get_all_children_from_group(session, group_id)
        if not user_ids:
            await query.message.answer(lexicon["not_child_group"])
            return
        buttons = []
        for user in user_ids:
            button = InlineKeyboardButton(
                text=user.name,
                callback_data=(
                    f"{user.name}, "
                    f"{user.group}, "
                    f"{user.score},"
                    f"{language}"
                ),
            )
            buttons.append([button])
        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await state.set_state(TaskState.buttons_child_info)
        await query.message.edit_text(
            lexicon["choose_child"], reply_markup=reply_markup
        )
    except IndexError:
        await query.message.answer(lexicon["not_child_group"])
        await state.clear()
    except Exception as err:
        await query.message.edit_text(lexicon["error_group"])
        logger.error(f"Произошла ошибка при поиске группы: {err}")
        await state.clear()


@router.callback_query(TaskState.buttons_child_info)
async def check_child_buttons(query: CallbackQuery, state: FSMContext):
    """Вывод информации о ребенке."""
    try:
        await query.answer()
        await state.clear()
        action = query.data.split(",")
        name = action[0]
        group = int(action[1])
        score = int(action[2])
        language = action[3]
        lexicon = LEXICON[language]
        await query.message.edit_text(
            f"{lexicon['child_name']} {name}, {lexicon['group_child']} "
            f"{group}, {lexicon['score_child']} {score},"
        )
    except Exception as err:
        await query.message.answer(lexicon["error_child"])
        logger.error(f"Произошла ошибка : {err}")
    finally:
        await state.clear()

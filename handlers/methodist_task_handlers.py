import logging
import time
from typing import Any

from aiogram import F, Router, handlers
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Chat,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
)

from handlers.handlers import BasePaginatedHandler
from keyboards.keyboards import pagination_keyboard, yes_no_keyboard
from keyboards.methodist_keyboards import (
    add_task_keyboard,
    artifact_type_keyboard,
    choice_tasks_for_review_keyboard,
    confirm_task_keyboard,
    continue_job_keyboard,
    edit_task_keyboard,
    methodist_profile_keyboard,
    review_keyboard_methodist,
    task_keyboard_methodist,
    task_type_keyboard,
)
from lexicon.lexicon import BUTTONS, LEXICON
from utils.db_commands import (
    approve_task,
    create_achievement,
    get_achievements_with_tasks,
    get_all_achievements,
    get_categories_with_tasks,
    get_tasks_by_achievement_and_status,
    get_tasks_by_achievement_category_and_status,
    get_tasks_by_status,
    get_user_achievement,
    reject_task,
    select_user,
    set_achievement_param,
)
from utils.pagination import PAGE_SIZE
from utils.states_form import AddTask, EditTask, ReviewTask, TaskList
from utils.user_utils import save_rejection_reason_in_db
from utils.utils import (
    generate_achievements_list,
    get_achievement_info,
    message_pattern,
    object_info,
    task_info,
)

logger = logging.getLogger(__name__)

methodist_task_router = Router()


class BasePaginatedTaskHandler(BasePaginatedHandler):
    async def delete_messages(self, media_group):
        for message_id in media_group:
            await Chat.delete_message(self.message.chat, message_id)

    async def handle(self) -> Any:
        await super().handle()
        try:
            if self.page_info is not None:
                task_ids = self.page_info["objects_ids"]
                new_current_page = self.page_info["current_page"]

                await self.fsm_state.set_state(TaskList.tasks_for_review)

                await self.fsm_state.update_data(
                    task_ids=task_ids,
                    language=self.language,
                    current_page=new_current_page,
                    task_info=self.page_info,
                    cd=self.cd,
                    query_id=self.query_id,
                )

            media_group = self.fsm_data.get("media_group")
            if media_group:
                await self.delete_messages(media_group)
                await self.fsm_state.update_data(media_group=None)

        except Exception as err:
            logger.error(f"Ошибка при проверке заданий методистом: {err}")


# Обработчики раздела с заданиями


@methodist_task_router.message(
    F.text.in_(
        [
            BUTTONS["RU"]["tasks_for_review"],
            BUTTONS["TT"]["tasks_for_review"],
            BUTTONS["EN"]["tasks_for_review"],
        ]
    )
)
class ChoiceTasksForReview(handlers.MessageHandler):
    """Выбор заданий на проверку."""

    async def handle(self) -> Any:
        try:
            fsm_state = self.data["state"]
            await fsm_state.clear()
            user = select_user(self.from_user.id)
            language = user.language
            lexicon = LEXICON[language]

            await fsm_state.update_data(language=language)
            await self.event.answer(
                text=lexicon["choice_tasks"],
                reply_markup=choice_tasks_for_review_keyboard(language),
            )
            await self.event.delete()

        except Exception as err:
            logger.error(f"Ошибка при выборе заданий методистом: {err}")


@methodist_task_router.callback_query(F.data == "back_tasks_for_review")
class ChoiceTasksForReviewCallback(handlers.CallbackQueryHandler):
    """Выбор заданий на проверку."""

    async def handle(self) -> Any:
        try:
            fsm_state = self.data["state"]
            fsm_data = await self.data["state"].get_data()
            language = fsm_data["language"]
            lexicon = LEXICON[language]

            await fsm_state.update_data(language=language)
            await self.message.edit_text(
                text=lexicon["choice_tasks"],
                reply_markup=choice_tasks_for_review_keyboard(language),
            )

        except Exception as err:
            logger.error(f"Ошибка при выборе заданий методистом: {err}")


@methodist_task_router.callback_query(
    F.data.in_(
        (
            "choice_category",
            "choice_category:next",
            "choice_category:previous",
            "back_choice_category",
        )
    )
)
class ChoiceCategoryForReviewCallback(BasePaginatedTaskHandler):
    """Выбор категории для проверки заданий."""

    cd = "choice_category"

    def get_queryset(self) -> Any:
        return get_categories_with_tasks("pending_methodist")

    @staticmethod
    def message_view(lexicon, text) -> str:
        header = "show_categories_with_tasks"
        footer = "choice_category"
        return message_pattern(lexicon, text, header, footer)

    @staticmethod
    def object_info(lexicon: dict, count: int, obj, *args, **kwargs) -> str:
        return object_info(lexicon, count, obj)

    def extra_buttons(self) -> dict:
        back_button = {
            "text": BUTTONS[self.language]["back"],
            "callback_data": "back_tasks_for_review",
        }
        return back_button


@methodist_task_router.callback_query(F.data.startswith("choice_category"))
@methodist_task_router.callback_query(
    F.data.in_(
        (
            "tasks_by_category",
            "tasks_by_category:next",
            "tasks_by_category:previous",
        )
    )
)
class TasksForReviewByCategoryCallback(BasePaginatedTaskHandler):
    """Ачивки по категориям, отправленные методисту на проверку."""

    cd = "tasks_by_category"

    def get_queryset(self) -> Any:
        return get_tasks_by_achievement_category_and_status(
            self.query_id, "pending_methodist"
        )

    @staticmethod
    def message_view(lexicon, text) -> str:
        header = "children_tasks"
        footer = "checkout_artifacts"
        return message_pattern(lexicon, text, header, footer)

    @staticmethod
    def object_info(lexicon: dict, count: int, obj, *args, **kwargs) -> str:
        return task_info(lexicon, count, obj)

    def extra_buttons(self) -> dict:
        back_button = {
            "text": BUTTONS[self.language]["back"],
            "callback_data": "back_choice_category",
        }
        return back_button


@methodist_task_router.callback_query(
    F.data.in_(
        (
            "choice_achievement",
            "choice_achievement:next",
            "choice_achievement:previous",
            "back_choice_achievement",
        )
    )
)
class ChoiceAchievementForReviewCallback(BasePaginatedTaskHandler):
    """Выбор ачивки для проверки."""

    cd = "choice_achievement"

    def get_queryset(self) -> Any:
        return get_achievements_with_tasks("pending_methodist")

    @staticmethod
    def message_view(lexicon, text) -> str:
        header = "show_achievement_with_tasks"
        footer = "choice_achievement"
        return message_pattern(lexicon, text, header, footer)

    @staticmethod
    def object_info(lexicon: dict, count: int, obj, *args, **kwargs) -> str:
        return object_info(lexicon, count, obj)

    def extra_buttons(self) -> dict:
        back_button = {
            "text": BUTTONS[self.language]["back"],
            "callback_data": "back_tasks_for_review",
        }
        return back_button


@methodist_task_router.callback_query(F.data.startswith("choice_achievement"))
@methodist_task_router.callback_query(
    F.data.in_(
        (
            "tasks_by_achievement",
            "tasks_by_achievement:next",
            "tasks_by_achievement:previous",
        )
    )
)
class TasksForReviewByAchievementCallback(BasePaginatedTaskHandler):
    """Задания на одну ачивку для проверки методистом."""

    cd = "tasks_by_achievement"

    def get_queryset(self) -> Any:
        return get_tasks_by_achievement_and_status(
            self.query_id, "pending_methodist"
        )

    @staticmethod
    def message_view(lexicon, text) -> str:
        header = "children_tasks"
        footer = "checkout_artifacts"
        return message_pattern(lexicon, text, header, footer)

    @staticmethod
    def object_info(lexicon: dict, count: int, obj, *args, **kwargs) -> str:
        return task_info(lexicon, count, obj)

    def extra_buttons(self) -> dict:
        back_button = {
            "text": BUTTONS[self.language]["back"],
            "callback_data": "back_choice_achievement",
        }
        return back_button


@methodist_task_router.callback_query(
    F.data.in_(("all_tasks", "all_tasks:next", "all_tasks:previous"))
)
class TasksForReviewCallback(BasePaginatedTaskHandler):
    """
    Обработчик кнопки Все задания.

    Показывает все ачивки, отправленные методисту на проверку в статусе
    "pending_methodist".
    """

    cd = "all_tasks"

    def get_queryset(self) -> Any:
        return get_tasks_by_status("pending_methodist")

    @staticmethod
    def message_view(lexicon, text) -> str:
        header = "children_tasks"
        footer = "checkout_artifacts"
        return message_pattern(lexicon, text, header, footer)

    @staticmethod
    def object_info(lexicon: dict, count: int, obj, *args, **kwargs) -> str:
        return task_info(lexicon, count, obj)

    def extra_buttons(self) -> dict:
        back_button = {
            "text": BUTTONS[self.language]["back"],
            "callback_data": "back_tasks_for_review",
        }
        return back_button


@methodist_task_router.callback_query(
    TaskList.tasks_for_review, F.data.startswith("all_tasks")
)
@methodist_task_router.callback_query(
    TaskList.tasks_for_review, F.data.startswith("tasks_by_achievement")
)
@methodist_task_router.callback_query(
    TaskList.tasks_for_review, F.data.startswith("tasks_by_category")
)
async def show_review_task(query: CallbackQuery, state: FSMContext):
    """Обработчик кнопок выбора отдельной ачивки на проверку.

    Получаем условный id ачивки из callback_data, достаем реальный id из
    состояние Data и получаем полную инфу об ачивке из базы данных.
    """

    async def input_media(
        files_id: list, InputMedia: InputMediaPhoto | InputMediaVideo
    ) -> list:
        media_group = []
        for file in files_id:
            media_group.append(InputMedia(media=file))
        return media_group

    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        cd = data["cd"]
        task_number = int(query.data.split(":")[-1])
        task_id = data["task_ids"][task_number]
        task = get_user_achievement(task_id)
        msg = (
            f"<b>{lexicon['review_user']}</b> {task.user.name}\n"
            f"***\n"
            f"<b>{lexicon['review_name']}</b> {task.achievement.name}\n"
            f"<b>{lexicon['review_description']}</b> "
            f"{task.achievement.description}\n"
            f"<b>{lexicon['review_instruction']}</b> "
            f"{task.achievement.instruction}\n"
            f"<b>{lexicon['review_type']}</b> "
            f"{task.achievement.achievement_type}\n"
            f"<b>{lexicon['review_artifact']}</b> "
            f"{task.achievement.artifact_type}\n"
        )

        if task.achievement.artifact_type == "text":
            msg = f"{task.message_text}\n\n" + msg
            await query.message.answer(
                msg, reply_markup=review_keyboard_methodist(language, cd=cd)
            )
        else:
            match task.achievement.artifact_type:
                case "image":
                    media = await input_media(task.files_id, InputMediaPhoto)
                case "video":
                    media = await input_media(task.files_id, InputMediaVideo)

            media_group = await query.message.answer_media_group(media=media)
            media_group = [message.message_id for message in media_group]

            await state.update_data(media_group=media_group)
            await query.message.answer(
                msg, reply_markup=review_keyboard_methodist(language, cd=cd)
            )

        await state.set_state(ReviewTask.pending)
        await state.update_data(task_id=task_id, language=language)
        await query.message.delete()

    except KeyError as err:
        logger.error(f"Проверь правильность ключевых слов: {err}")
    except Exception as err:
        logger.error(f"Ошибка при получении ачивки: {err}")


@methodist_task_router.callback_query(ReviewTask.pending, F.data == "approve")
async def approve_methodist_handler(query: CallbackQuery, state: FSMContext):
    """Принять задание."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        task_id = data["task_id"]
        cd = data["cd"]
        msg = f'{lexicon["failed_to_find_task"]} {task_id}.'

        if approve_task(task_id):
            msg = f'{lexicon["task_approved"]}: {task_id}.'

        await state.update_data(media_group=None)
        await query.message.answer(
            msg, reply_markup=continue_job_keyboard(language, cd)
        )

    except Exception as err:
        logger.error(f"Произошла ошибка при подтверждении задания: {err}")
        await query.message.answer(
            "Произошла ошибка при подтверждении задания."
        )


@methodist_task_router.callback_query(ReviewTask.pending, F.data == "reject")
async def reject_methodist_handler(query: CallbackQuery, state: FSMContext):
    """Отклонить задание."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        task_id = data["task_id"]
        cd = data["cd"]
        msg = f'{lexicon["failed_to_find_task"]} {task_id}.'

        if reject_task(task_id):
            await query.message.answer(
                f'{lexicon["task_rejected"]}',
                reply_markup=yes_no_keyboard(language, "methodist_check_task"),
            )

        else:
            await query.message.edit_text(
                msg, reply_markup=continue_job_keyboard(language, cd)
            )
        await state.update_data(media_group=None)

    except Exception as err:
        logger.error(f"Произошла ошибка при отклонении задания: {err}")
        await query.message.answer("Произошла ошибка при отклонении задания.")


@methodist_task_router.callback_query(
    ReviewTask.pending, F.data == "yes:methodist_check_task"
)
async def yes_methodist_handler(query: CallbackQuery, state: FSMContext):
    """Обработка кнопки 'Да' при отклонении задания."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        task_id = data["task_id"]

        await state.set_state(ReviewTask.reject_message)
        await state.update_data(task_id=task_id)
        await query.message.edit_text(f'{lexicon["give_rejection_reason"]}')

    except Exception as err:
        logger.error(f"Произошла ошибка при обработке запроса: {err}")
        await query.message.answer("Произошла ошибка при обработке запроса.")


@methodist_task_router.callback_query(
    ReviewTask.pending, F.data == "no:methodist_check_task"
)
async def no_methodist_handler(query: CallbackQuery, state: FSMContext):
    """Обработка кнопки 'Нет' при отклонении задания."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        cd = data["cd"]

        await query.message.edit_text(
            lexicon["no_rejection_reason"],
            reply_markup=continue_job_keyboard(language, cd),
        )

    except Exception as err:
        logger.error(f"Произошла ошибка при обработке запроса: {err}")
        await query.message.answer("Произошла ошибка при обработке запроса.")


@methodist_task_router.message(ReviewTask.reject_message)
async def rejection_reason(message: Message, state: FSMContext):
    """Сохраняет причину отклонения задания."""
    try:
        data = await state.get_data()
        task_id = data.get("task_id")
        language = data["language"]
        lexicon = LEXICON[language]
        cd = data["cd"]

        if message.text.lower() != "отмена":
            save_rejection_reason_in_db(task_id, message.text)
            await message.answer(
                lexicon["rejection_reason_saved"],
                reply_markup=continue_job_keyboard(language, cd),
            )
        else:
            await message.answer(
                lexicon["no_rejection_reason"],
                reply_markup=continue_job_keyboard(language, cd),
            )

        await state.set_state(state=None)

    except Exception as err:
        logger.error(f"Произошла ошибка при обработке запроса: {err}")
        await message.answer("Произошла ошибка при обработке запроса.")


# Обработчики добавления задания
@methodist_task_router.message(
    F.text.in_(
        [
            BUTTONS["RU"]["add_task"],
            BUTTONS["TT"]["add_task"],
            BUTTONS["EN"]["add_task"],
        ]
    )
)
async def add_task(message: Message):
    """Обработчик кнопки Добавить задание."""
    try:
        user = select_user(message.from_user.id)
        language = user.language
        lexicon = LEXICON[language]
        await message.answer(
            lexicon["add_task"], reply_markup=add_task_keyboard(language)
        )
    except KeyError as err:
        logger.error(f"Ошибка в ключе при добавлении задания в базу: {err}")
    except Exception as err:
        logger.error(f"Ошибка при добавлении задания в базу: {err}")


@methodist_task_router.callback_query(F.data == "ready")
async def start_add_task(query: CallbackQuery, state: FSMContext):
    """Начинает сценарий добавления ачивки в базу."""
    try:
        await query.answer()
        await state.clear()
        user = select_user(query.from_user.id)
        language = user.language
        lexicon = LEXICON[language]
        await state.update_data(language=language)
        await state.set_state(AddTask.name)
        await query.message.answer(lexicon["send_task_name"])
        await query.message.delete()
    except KeyError as err:
        logger.error(f"Ошибка в ключе при запросе названия ачивки: {err}")
    except Exception as err:
        logger.error(f"Ошибка при запросе названия ачивки: {err}")


@methodist_task_router.message(AddTask.name)
async def process_add_task_name(message: Message, state: FSMContext):
    """Принимает название ачивки, запрашивает описание."""
    try:
        data = await state.get_data()
        language = data["language"]
        await state.update_data(name=message.text)
        await state.set_state(AddTask.description)
        await message.answer(LEXICON[language]["send_task_description"])
    except KeyError as err:
        logger.error(f"Ошибка в ключе при запросе описания ачивки: {err}")
    except Exception as err:
        logger.error(f"Ошибка при запросе описания ачивки: {err}")


@methodist_task_router.message(AddTask.description)
async def process_add_task_description(message: Message, state: FSMContext):
    """Принимает описание ачивки, запрашивает инструкцию."""
    try:
        data = await state.get_data()
        language = data["language"]
        await state.update_data(description=message.text)
        await state.set_state(AddTask.instruction)
        await message.answer(LEXICON[language]["send_task_instruction"])
    except KeyError as err:
        logger.error(
            f"Ошибка в ключе при запросе инструкции для ачивки: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при запросе инструкции для ачивки: {err}")


@methodist_task_router.message(AddTask.instruction)
async def process_add_task_instruction(message: Message, state: FSMContext):
    """Принимает инструкцию ачивки, запрашивает колв-во начисляемых баллов."""
    try:
        data = await state.get_data()
        language = data["language"]
        await state.update_data(instruction=message.text)
        await state.set_state(AddTask.score)
        await message.answer(LEXICON[language]["send_task_score"])
    except KeyError as err:
        logger.error(f"Ошибка в ключе при запросе баллов ачивки: {err}")
    except Exception as err:
        logger.error(f"Ошибка при запросе баллов ачивки: {err}")


@methodist_task_router.message(AddTask.score)
async def process_add_task_score(message: Message, state: FSMContext):
    """Принимает кол-во начисляемых баллов за ачивку.

    Запрашивает кол-во баллов для открытия ачивки.
    """
    try:
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        await state.update_data(score=int(message.text))
        await state.set_state(AddTask.price)
        await message.answer(lexicon["send_task_price"])
    except KeyError as err:
        logger.error(f"Ошибка в ключе при запросе баллов ачивки: {err}")
    except ValueError as err:
        logger.error(f"Неправильный тип данных для баллов: {err}")
        await state.set_state(AddTask.score)
        await message.answer(lexicon["ask_number_again"])
    except Exception as err:
        logger.error(f"Ошибка при запросе баллов ачивки: {err}")


@methodist_task_router.message(AddTask.price)
async def process_add_task_price(message: Message, state: FSMContext):
    """Принимает кол-во баллов для открытия ачивки, запрашивает тип ачивки."""
    try:
        data = await state.get_data()
        language = data["language"]
        lexicon = LEXICON[language]
        await state.update_data(price=int(message.text))
        await state.set_state(AddTask.achievement_type)
        await message.answer(
            lexicon["send_task_type"],
            reply_markup=task_type_keyboard(language),
        )
    except KeyError as err:
        logger.error(
            f"Ошибка в ключе при запросе баллов для открытия ачивки: {err}"
        )
    except ValueError as err:
        logger.error(f"Неправильный тип данных для баллов: {err}")
        await state.set_state(AddTask.price)
        await message.answer(lexicon["ask_number_again"])
    except Exception as err:
        logger.error(f"Ошибка при запросе баллов для открытия ачивки: {err}")


@methodist_task_router.callback_query(AddTask.achievement_type)
async def process_add_task_type(query: CallbackQuery, state: FSMContext):
    """Принимает тип ачивки, запрашивает тип артефакта."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        await state.update_data(achievement_type=query.data)
        await state.set_state(AddTask.artifact_type)
        await query.message.edit_text(
            LEXICON[language]["send_task_artifact_type"],
            reply_markup=artifact_type_keyboard(language),
        )
    except KeyError as err:
        logger.error(f"Ошибка в ключе при запросе баллов ачивки: {err}")
    except Exception as err:
        logger.error(f"Ошибка при запросе баллов ачивки: {err}")


@methodist_task_router.callback_query(AddTask.artifact_type)
async def process_add_task_artifact_type(
    query: CallbackQuery, state: FSMContext
):
    """Принимает тип артефакта, запрашивает изображение для ачивки."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        await state.update_data(artifact_type=query.data)
        await state.set_state(AddTask.image)
        await query.message.edit_text(LEXICON[language]["send_task_image"])
    except KeyError as err:
        logger.error(f"Ошибка в ключе при запросе баллов ачивки: {err}")
    except Exception as err:
        logger.error(f"Ошибка при запросе баллов ачивки: {err}")


@methodist_task_router.message(AddTask.image)
async def process_add_task_image(message: Message, state: FSMContext):
    """Принимает изображение для ачивки, сохраняет ачивку в БД.

    Отправляет собранные данные для подтверждения корректности или для
    перехода к редактированию.
    """
    try:
        data = await state.get_data()
        await state.clear()
        language = data["language"]
        lexicon = LEXICON[language]
        if not message.photo:
            await state.set_state(AddTask.image)
            await message.answer(lexicon["ask_image_again"])
            return
        data["image"] = message.photo[0].file_id
        task_created = create_achievement(data)
        if not task_created:
            await message.answer(
                lexicon["error_adding_task"],
                reply_markup=methodist_profile_keyboard(language),
            )
            return
        task_info = get_achievement_info(data["name"], lexicon)
        info = task_info["info"]
        image = task_info["image"]
        task_id = task_info["id"]
        # Собираем пагинацию для списка ачивок, если пользователь
        # перейдет к редактированию созданной ачивки
        tasks = get_all_achievements()
        page_info = generate_achievements_list(
            tasks=tasks, lexicon=lexicon, current_page=0, page_size=PAGE_SIZE
        )
        task_ids = page_info["task_ids"]
        new_current_page = page_info["current_page"]
        query_id = None
        for key in task_ids.keys():
            if task_ids[key] == task_id:
                query_id = key
        await state.set_state(EditTask.confirm_task)
        await state.update_data(
            task_id=task_id,
            query_id=query_id,
            tasks=tasks,
            task_ids=task_ids,
            current_page=new_current_page,
            task_info=page_info,
            language=language,
        )
        # Сообщаем пользователю, что сейчас покажем, что получилось
        await message.answer(lexicon["confirm_adding_task"])
        time.sleep(2)
        # Показываем, что получилось
        await message.answer_photo(
            photo=image,
            caption=info,
            reply_markup=confirm_task_keyboard(language),
        )
    except KeyError as err:
        logger.error(f"Ошибка в ключе при запросе подтверждения ачивки: {err}")
    except Exception as err:
        logger.error(f"Ошибка при запросе подтверждения ачивки: {err}")


@methodist_task_router.callback_query(
    EditTask.confirm_task, F.data == "confirm"
)
async def process_saving_task_to_db(query: CallbackQuery, state: FSMContext):
    """Обработчик кнопки Подтверждаю."""
    try:
        await query.answer()
        data = await state.get_data()
        await state.clear()
        language = data["language"]
        lexicon = LEXICON[language]
        await query.message.answer(
            lexicon["task_added"],
            reply_markup=methodist_profile_keyboard(language),
        )
        await query.message.delete()
    except KeyError as err:
        logger.error(f"Ошибка в ключе при добавлении ачивки: {err}")
    except Exception as err:
        logger.error(f"Ошибка при добавлении ачивки: {err}")


# Обработчики редактирования задания
@methodist_task_router.message(
    F.text.in_(
        [
            BUTTONS["RU"]["achievement_list"],
            BUTTONS["TT"]["achievement_list"],
            BUTTONS["EN"]["achievement_list"],
        ]
    )
)
async def show_task_list(message: Message, state: FSMContext):
    """Обработчик кнопки Посмотреть/редактировать ачивки.

    Показывает все созданные ачивки с пагинацией.
    """
    try:
        await state.clear()
        user = select_user(message.from_user.id)
        language = user.language
        lexicon = LEXICON[language]
        tasks = get_all_achievements()
        if not tasks:
            await message.answer(
                lexicon["no_tasks_yet"],
                reply_markup=add_task_keyboard(language),
            )
            return
        current_page = 1
        page_info = generate_achievements_list(
            tasks=tasks,
            lexicon=lexicon,
            current_page=current_page,
            page_size=PAGE_SIZE,
            methodist=True,
        )
        msg = page_info["msg"]
        task_ids = page_info["task_ids"]
        first_item = page_info["first_item"]
        final_item = page_info["final_item"]
        lk_button = {
            "text": BUTTONS[language]["lk"],
            "callback_data": "profile",
        }
        await state.set_state(TaskList.tasks)
        await state.update_data(
            tasks=tasks,
            task_ids=task_ids,
            current_page=current_page,
            task_info=page_info,
            language=language,
        )
        await message.answer(
            msg,
            reply_markup=pagination_keyboard(
                buttons_count=len(tasks),
                start=first_item,
                end=final_item,
                cd="task",
                page_size=PAGE_SIZE,
                extra_button=lk_button,
            ),
        )
    except KeyError as err:
        logger.error(f"Ошибка в ключе при просмотре списка заданий: {err}")
    except Exception as err:
        logger.error(f"Ошибка при просмотре списка заданий: {err}")


@methodist_task_router.callback_query(
    F.data.in_(["back_to_achievement_list", "task:next", "task:previous"])
)
async def show_task_list_callback(query: CallbackQuery, state: FSMContext):
    """Обработчик кнопки Посмотреть/редактировать ачивки.

    Показывает все созданные ачивки с пагинацией.
    """
    try:
        await query.answer()
        data = await state.get_data()
        tasks = data["tasks"]
        current_page = data["current_page"]
        language = data["language"]
        lexicon = LEXICON[language]
        if query.data == "task:next":
            current_page += 1
        elif query.data == "task:previous":
            current_page -= 1
        page_info = generate_achievements_list(
            tasks=tasks,
            lexicon=lexicon,
            current_page=current_page,
            page_size=PAGE_SIZE,
            methodist=True,
        )
        msg = page_info["msg"]
        first_item = page_info["first_item"]
        final_item = page_info["final_item"]
        new_current_page = page_info["current_page"]
        lk_button = {
            "text": BUTTONS[language]["lk"],
            "callback_data": "profile",
        }
        await state.set_state(TaskList.tasks)
        await state.update_data(
            tasks=tasks, current_page=new_current_page, task_info=page_info
        )
        if query.data == "back_to_achievement_list":
            # Возвращаемся со страницы ачивки с фото,
            # текст нельзя редактировать
            await query.message.answer(
                msg,
                reply_markup=pagination_keyboard(
                    buttons_count=len(tasks),
                    start=first_item,
                    end=final_item,
                    cd="task",
                    page_size=PAGE_SIZE,
                    extra_button=lk_button,
                ),
            )
            await query.message.delete()
            return
        await query.message.edit_text(
            msg,
            reply_markup=pagination_keyboard(
                buttons_count=len(tasks),
                start=first_item,
                end=final_item,
                cd="task",
                page_size=PAGE_SIZE,
                extra_button=lk_button,
            ),
        )
    except KeyError as err:
        logger.error(f"Ошибка в ключе при просмотре списка заданий: {err}")
    except Exception as err:
        logger.error(f"Ошибка при просмотре списка заданий: {err}")


@methodist_task_router.callback_query(
    TaskList.tasks, F.data.startswith("task:")
)
@methodist_task_router.callback_query(F.data.startswith("back_to_task:"))
async def show_task(query: CallbackQuery, state: FSMContext):
    """Обработчик кнопок выбора отдельной ачивки.

    Получаем условный id ачивки из callback_data, достаем реальный id из
    состояние Data и получаем полную инфу об ачивке из базы данных.
    """
    try:
        await query.answer()
        data = await state.get_data()
        if not data:
            user = select_user(query.from_user.id)
            await query.message.answer(
                LEXICON[user.language]["error_getting_achievement"],
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=task_keyboard_methodist(user.language)
                ),
            )
            return
        language = data["language"]
        lexicon = LEXICON[language]
        task_number = int(query.data.split(":")[-1])
        # Достаем id ачивки из состояния и делаем запрос к базе
        task_id = data["task_ids"][task_number]
        # Получаем текст для сообщения и изображение ачивки
        info_image = get_achievement_info(task_id, lexicon)
        info = info_image["info"]
        image = info_image["image"]
        msg = f'{lexicon["achievement_chosen"]}\n\n' f"{info}\n\n"
        await state.set_state(EditTask.task_id)
        await state.update_data(task_id=task_id, query_id=task_number)
        if not image:
            await query.message.edit_text(
                msg, reply_markup=task_keyboard_methodist(language)
            )
            return
        await query.message.answer_photo(
            photo=image,
            caption=msg,
            reply_markup=task_keyboard_methodist(language),
        )
        await query.message.delete()
    except KeyError as err:
        logger.error(f"Ошибка в ключевом слове при получении ачивки: {err}")
    except Exception as err:
        logger.error(f"Ошибка при получении ачивки: {err}")


# Блок редактирования ачивки
@methodist_task_router.callback_query(F.data == "complete_editing")
async def process_complete_editing(query: CallbackQuery, state: FSMContext):
    """Завершает сценарий редактирования задания."""
    try:
        await query.answer()
        data = await state.get_data()
        await state.clear()
        language = data["language"]
        lexicon = LEXICON[language]
        await query.message.answer(
            lexicon["editing_completed"],
            reply_markup=methodist_profile_keyboard(language),
        )
        await query.message.delete()
    except KeyError as err:
        logger.error(
            f"Ошибка в ключе при завершении редактирования ачивки: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при завершении редактирования ачивки: {err}")


@methodist_task_router.callback_query(EditTask.task_id, F.data == "edit_task")
@methodist_task_router.callback_query(
    EditTask.confirm_task, F.data == "edit_task"
)
async def process_edit_task(query: CallbackQuery, state: FSMContext):
    """Обработчик инлайн кнопки 'Редактировать задание'.

    Начинает сценарий внесения изменений в базу.
    """
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        query_id = data["query_id"]
        lexicon = LEXICON[language]
        await query.message.answer(
            lexicon["start_edit_task"],
            reply_markup=edit_task_keyboard(language, cd=query_id),
        )
        await query.message.delete()
    except KeyError as err:
        logger.error(
            f"Ошибка в ключе при начале редактирования задания: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при начале редактирования задания: {err}")


@methodist_task_router.callback_query(F.data == "edit_name")
async def edit_name(query: CallbackQuery, state: FSMContext):
    """Обработчик создает состояние для смены названия ачивки.

    Просит прислать сообщение.
    """
    try:
        await query.answer()
        data = await state.get_data()
        await state.set_state(EditTask.name)
        language = data["language"]
        lexicon = LEXICON[language]
        await query.message.answer(lexicon["edit_task_name"])
        await query.message.delete()
    except KeyError as err:
        logger.error(
            "Ошибка в ключевом слове при запросе нового "
            f"названия ачивки: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при запросе нового названия ачивки: {err}")


@methodist_task_router.message(EditTask.name)
async def process_edit_name(message: Message, state: FSMContext):
    """Обрабатывает сообщение для изменения названия ачивки."""
    try:
        data = await state.get_data()
        language = data["language"]
        query_id = data["query_id"]
        lexicon = LEXICON[language]
        task_saved = set_achievement_param(
            achievement_id=data["task_id"], name=message.text
        )
        if not task_saved:
            await message.answer(
                lexicon["error_adding_task"],
                reply_markup=methodist_profile_keyboard(language),
            )
            return
        await message.answer(
            lexicon["task_edited"],
            reply_markup=edit_task_keyboard(language, cd=query_id),
        )
    except KeyError as err:
        logger.error(
            f"Ошибка в ключевом слове при изменении названия ачивк: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при изменении названия ачивк: {err}")


@methodist_task_router.callback_query(F.data == "edit_image")
async def change_image(query: CallbackQuery, state: FSMContext):
    """Обработчик создает состояние для смены изображения ачивки.

    Просит прислать фото.
    """
    try:
        await query.answer()
        data = await state.get_data()
        await state.set_state(EditTask.image)
        language = data["language"]
        lexicon = LEXICON[language]
        await query.message.answer(lexicon["edit_task_image"])
        await query.message.delete()
    except KeyError as err:
        logger.error(
            "Ошибка в ключевом слове при запросе нового " f"фото ачивки: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при запросе нового фото ачивки: {err}")


@methodist_task_router.message(EditTask.image)
async def process_change_image(message: Message, state: FSMContext):
    """Обрабатывает сообщение для изменения изображения ачивки."""
    try:
        data = await state.get_data()
        language = data["language"]
        query_id = data["query_id"]
        lexicon = LEXICON[language]
        if not message.photo:
            await state.set_state(EditTask.image)
            await message.answer(lexicon["ask_image_again"])
            return
        new_image = message.photo[-1].file_id
        task_saved = set_achievement_param(
            achievement_id=data["task_id"], image=new_image
        )
        if not task_saved:
            await message.answer(
                lexicon["error_adding_task"],
                reply_markup=methodist_profile_keyboard(language),
            )
            return
        await message.answer(
            lexicon["task_edited"],
            reply_markup=edit_task_keyboard(language, cd=query_id),
        )
    except KeyError as err:
        logger.error(
            f"Ошибка в ключевом слове при изменении фото ачивки: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при изменении фото ачивки: {err}")


@methodist_task_router.callback_query(F.data == "edit_description")
async def change_description(query: CallbackQuery, state: FSMContext):
    """Обработчик создает состояние для смены описания ачивки.

    Просит прислать текст.
    """
    try:
        await query.answer()
        data = await state.get_data()
        await state.set_state(EditTask.description)
        language = data["language"]
        lexicon = LEXICON[language]
        await query.message.answer(lexicon["edit_task_description"])
        await query.message.delete()
    except KeyError as err:
        logger.error(
            "Ошибка в ключевом слове при запросе нового "
            f"описания ачивки: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при запросе нового описания ачивки: {err}")


@methodist_task_router.message(EditTask.description)
async def process_change_description(message: Message, state: FSMContext):
    """Обрабатывает сообщение для изменения описания ачивки."""
    try:
        data = await state.get_data()
        language = data["language"]
        query_id = data["query_id"]
        lexicon = LEXICON[language]
        task_saved = set_achievement_param(
            achievement_id=data["task_id"], description=message.text
        )
        if not task_saved:
            await message.answer(
                lexicon["error_adding_task"],
                reply_markup=methodist_profile_keyboard(language),
            )
            return
        await message.answer(
            lexicon["task_edited"],
            reply_markup=edit_task_keyboard(language, cd=query_id),
        )
    except KeyError as err:
        logger.error(
            f"Ошибка в ключевом слове при изменении описания ачивки: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при изменении описания ачивки: {err}")


@methodist_task_router.callback_query(F.data == "edit_instruction")
async def change_instruction(query: CallbackQuery, state: FSMContext):
    """Обработчик создает состояние для смены инструкции ачивки.

    Просит прислать текст.
    """
    try:
        await query.answer()
        data = await state.get_data()
        await state.set_state(EditTask.instruction)
        language = data["language"]
        lexicon = LEXICON[language]
        await query.message.answer(lexicon["edit_task_instruction"])
        await query.message.delete()
    except KeyError as err:
        logger.error(
            "Ошибка в ключевом слове при запросе новоой "
            f"инструкции ачивки: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при запросе новой инструкции ачивки: {err}")


@methodist_task_router.message(EditTask.instruction)
async def process_change_instruction(message: Message, state: FSMContext):
    """Обрабатывает сообщение для изменения инструкции ачивки."""
    try:
        data = await state.get_data()
        language = data["language"]
        query_id = data["query_id"]
        lexicon = LEXICON[language]
        task_saved = set_achievement_param(
            achievement_id=data["task_id"], instruction=message.text
        )
        if not task_saved:
            await message.answer(
                lexicon["error_adding_task"],
                reply_markup=methodist_profile_keyboard(language),
            )
            return
        await message.answer(
            lexicon["task_edited"],
            reply_markup=edit_task_keyboard(language, cd=query_id),
        )
    except KeyError as err:
        logger.error(
            f"Ошибка в ключевом слове при изменении инструкции ачивки: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при изменении инструкции ачивки: {err}")


@methodist_task_router.callback_query(F.data == "edit_score")
async def change_score(query: CallbackQuery, state: FSMContext):
    """Обработчик создает состояние для смены баллов ачивки.

    Просит прислать число.
    """
    try:
        await query.answer()
        data = await state.get_data()
        await state.set_state(EditTask.score)
        language = data["language"]
        lexicon = LEXICON[language]
        await query.message.answer(lexicon["edit_task_score"])
        await query.message.delete()
    except KeyError as err:
        logger.error(
            "Ошибка в ключевом слове при запросе новых "
            f"баллов ачивки: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при запросе новых баллов ачивки: {err}")


@methodist_task_router.message(EditTask.score)
async def process_change_score(message: Message, state: FSMContext):
    """Обрабатывает сообщение для изменения баллов ачивки."""
    try:
        data = await state.get_data()
        language = data["language"]
        query_id = data["query_id"]
        lexicon = LEXICON[language]
        task_saved = set_achievement_param(
            achievement_id=data["task_id"], score=int(message.text)
        )
        if not task_saved:
            await message.answer(
                lexicon["error_adding_task"],
                reply_markup=edit_task_keyboard(language, cd=query_id),
            )
            return
        await message.answer(
            lexicon["task_edited"], reply_markup=edit_task_keyboard(language)
        )
    except KeyError as err:
        logger.error(
            f"Ошибка в ключевом слове при изменении баллов ачивки: {err}"
        )
    except ValueError as err:
        logger.error(f"Неправильный тип данных для баллов: {err}")
        await state.set_state(EditTask.score)
        await message.answer(lexicon["ask_number_again"])
    except Exception as err:
        logger.error(f"Ошибка при изменении баллов ачивки: {err}")


@methodist_task_router.callback_query(F.data == "edit_price")
async def change_price(query: CallbackQuery, state: FSMContext):
    """Обработчик создает состояние для смены стоимости ачивки.

    Просит прислать число.
    """
    try:
        await query.answer()
        data = await state.get_data()
        await state.set_state(EditTask.price)
        language = data["language"]
        lexicon = LEXICON[language]
        await query.message.answer(lexicon["edit_task_price"])
        await query.message.delete()
    except KeyError as err:
        logger.error(
            "Ошибка в ключевом слове при запросе новой "
            f"стоимости ачивки: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при запросе новой стоимости ачивки: {err}")


@methodist_task_router.message(EditTask.price)
async def process_change_price(message: Message, state: FSMContext):
    """Обрабатывает сообщение для изменения стоимости ачивки."""
    try:
        data = await state.get_data()
        language = data["language"]
        query_id = data["query_id"]
        lexicon = LEXICON[language]
        task_saved = set_achievement_param(
            achievement_id=data["task_id"], price=int(message.text)
        )
        if not task_saved:
            await message.answer(
                lexicon["error_adding_task"],
                reply_markup=methodist_profile_keyboard(language),
            )
            return
        await message.answer(
            lexicon["task_edited"],
            reply_markup=edit_task_keyboard(language, cd=query_id),
        )
    except KeyError as err:
        logger.error(
            f"Ошибка в ключевом слове при изменении стоимости ачивки: {err}"
        )
    except ValueError as err:
        logger.error(f"Неправильный тип данных для стоимости: {err}")
        await state.set_state(EditTask.price)
        await message.answer(lexicon["ask_number_again"])
    except Exception as err:
        logger.error(f"Ошибка при изменении стоимости ачивки: {err}")


@methodist_task_router.callback_query(F.data == "edit_task_type")
async def change_task_type(query: CallbackQuery, state: FSMContext):
    """Обработчик создает состояние для смены типа ачивки.

    Предлагает выбрать из кнопок.
    """
    try:
        await query.answer()
        data = await state.get_data()
        await state.set_state(EditTask.achievement_type)
        language = data["language"]
        lexicon = LEXICON[language]
        await query.message.edit_text(
            lexicon["edit_task_type"],
            reply_markup=task_type_keyboard(language),
        )
    except KeyError as err:
        logger.error(
            "Ошибка в ключевом слове при запросе нового " f"типа ачивки: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при запросе нового типа ачивки: {err}")


@methodist_task_router.callback_query(EditTask.achievement_type)
async def process_change_task_type(query: CallbackQuery, state: FSMContext):
    """Принимает тип ачивки."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        query_id = data["query_id"]
        lexicon = LEXICON[language]
        task_saved = set_achievement_param(
            achievement_id=data["task_id"], achievement_type=query.data
        )
        if not task_saved:
            await query.message.answer(
                lexicon["error_adding_task"],
                reply_markup=methodist_profile_keyboard(language),
            )
            return
        await query.message.edit_text(
            lexicon["task_edited"],
            reply_markup=edit_task_keyboard(language, cd=query_id),
        )
    except KeyError as err:
        logger.error(f"Ошибка в ключе при обработке типа ачивки: {err}")
    except Exception as err:
        logger.error(f"Ошибка при обработке типа ачивки: {err}")


@methodist_task_router.callback_query(F.data == "edit_artifact_type")
async def change_artifact_type(query: CallbackQuery, state: FSMContext):
    """Обработчик создает состояние для смены типа артефакта.

    Предлагает выбрать из кнопок.
    """
    try:
        await query.answer()
        data = await state.get_data()
        await state.set_state(EditTask.artifact_type)
        language = data["language"]
        lexicon = LEXICON[language]
        await query.message.edit_text(
            lexicon["edit_task_artifact_type"],
            reply_markup=artifact_type_keyboard(language),
        )
    except KeyError as err:
        logger.error(
            "Ошибка в ключевом слове при запросе нового "
            f"типа артефакт: {err}"
        )
    except Exception as err:
        logger.error(f"Ошибка при запросе нового типа артефакта: {err}")


@methodist_task_router.callback_query(EditTask.artifact_type)
async def process_change_artifact_type(
    query: CallbackQuery, state: FSMContext
):
    """Принимает тип артефакта."""
    try:
        await query.answer()
        data = await state.get_data()
        language = data["language"]
        query_id = data["query_id"]
        lexicon = LEXICON[language]
        task_saved = set_achievement_param(
            achievement_id=data["task_id"], artifact_type=query.data
        )
        if not task_saved:
            await query.message.answer(
                lexicon["error_adding_task"],
                reply_markup=methodist_profile_keyboard(language),
            )
            return
        await query.message.edit_text(
            lexicon["task_edited"],
            reply_markup=edit_task_keyboard(language, cd=query_id),
        )
    except KeyError as err:
        logger.error(f"Ошибка в ключе при изменении типа артефакта: {err}")
    except Exception as err:
        logger.error(f"Ошибка при сохранении типа артефакта: {err}")

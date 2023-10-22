import logging
from typing import Any

from aiogram import handlers
from aiogram.types.chat import Chat

from keyboards.keyboards import pagination_keyboard
from lexicon.lexicon import LEXICON
from utils.utils import generate_objects_list

logger = logging.getLogger(__name__)


class BasePaginatedHandler(handlers.CallbackQueryHandler):
    """Базовый класс с пагинацией."""

    cd: str
    query_id: int = None
    language: str = None
    fsm_state: Any = None
    fsm_data: Any = None
    page_info: dict = None

    def get_queryset(self) -> Any:
        raise NotImplementedError

    @staticmethod
    def message_view(lexicon, text) -> str:
        """Шаблон сообщения."""
        raise NotImplementedError

    @staticmethod
    def object_info(lexicon: dict, count: int, obj, *args, **kwargs) -> str:
        """Шаблон объекта в сообщении."""
        raise NotImplementedError

    def extra_buttons(self) -> dict | None:
        """Дополнительные кнопки"""
        return None

    async def delete_messages(self, media_group):
        for message_id in media_group:
            await Chat.delete_message(self.message.chat, message_id)

    async def handle(self) -> Any:
        try:
            self.fsm_state = self.data["state"]
            self.fsm_data = await self.data["state"].get_data()
            self.language = self.fsm_data["language"]
            lexicon = LEXICON[self.language]
            current_page = self.fsm_data.get("current_page", 1)
            task_number = self.callback_data.split(":")[-1]

            if task_number.isdigit():
                self.query_id = self.fsm_data["task_ids"][int(task_number)]
            else:
                self.query_id = self.fsm_data.get("query_id")

            if self.callback_data == f"{self.cd}:next":
                current_page += 1
            elif self.callback_data == f"{self.cd}:previous":
                current_page -= 1

            query_set = self.get_queryset()

            if not query_set:
                msg = lexicon["nothing"]
                await self.event.answer(msg)

            else:
                self.page_info = generate_objects_list(
                    objects=query_set,
                    lexicon=lexicon,
                    msg=self.message_view,
                    obj_info=self.object_info,
                    current_page=current_page,
                )

                msg = self.page_info["msg"]
                first_item = self.page_info["first_item"]
                final_item = self.page_info["final_item"]

                await self.message.edit_text(
                    msg,
                    reply_markup=pagination_keyboard(
                        buttons_count=len(query_set),
                        start=first_item,
                        end=final_item,
                        cd=self.cd,
                        extra_button=self.extra_buttons(),
                    ),
                )

        except Exception as err:
            logger.error(f"Ошибка: {err}")

import asyncio
import logging

from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Union

logger = logging.getLogger(__name__)


class AcceptMediaGroupMiddleware(BaseMiddleware):
    """Middleware для обработки медиа группы."""

    def __init__(self, latency: Union[int, float] = 0.01):
        self.media_group = {}
        self.latency = latency
        super().__init__()

    async def _set_media_group_as_handled(self, media_group_id: str):
        try:
            _ = self.media_group[media_group_id]
            return False
        except KeyError:
            self.media_group[media_group_id] = []
            return True

    async def _get_media_group(
        self,
        media_group_id: str,
        handler: Callable[Message, Dict[str, Any]],
        event: Message,
        data: Dict[str, Any]
    ):
        data["album"] = self.media_group[media_group_id]
        data["media_group"] = media_group_id
        del self.media_group[media_group_id]
        return await handler(event, data)

    async def __call__(
        self,
        handler: Callable[Message, Dict[str, Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        try:
            loop = asyncio.get_running_loop()
            media_group_id = event.media_group_id
            if await self._set_media_group_as_handled(media_group_id):
                loop.call_later(
                    self.latency,
                    asyncio.create_task,
                    self._get_media_group(
                        media_group_id, handler, event, data)
                )
            self.media_group[media_group_id].append(event)
        except Exception as err:
            logger.error(
                f'Ошибка в мидлваре при обработке группы медиа: {err}')

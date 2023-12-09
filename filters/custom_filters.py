from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import Session

from db.models import User


class IsStudent(BaseFilter):
    """Проверяет id пользователя в базе детей."""

    async def __call__(
        self, message: Union[Message, CallbackQuery], session: Session
    ):
        PERSONAL = [
            user.id
            for user in session.query(User).filter(User.role != "kid").all()
        ]
        return message.from_user.id not in PERSONAL


class IsMethodist(BaseFilter):
    """Проверяет id пользователя в базе методистов."""

    async def __call__(
        self, message: Union[Message, CallbackQuery], session: Session
    ):
        METHODISTS = [
            user.id
            for user in session.query(User)
            .filter(User.role == "methodist")
            .all()
        ]
        return message.from_user.id in METHODISTS


class IsCounselour(BaseFilter):
    """Проверяет id пользователя в базе вожатых."""

    async def __call__(
        self, message: Union[Message, CallbackQuery], session: Session
    ):
        COUNSELOURS = [
            user.id
            for user in session.query(User)
            .filter(User.role == "counsellor")
            .all()
        ]
        return message.from_user.id in COUNSELOURS

from aiogram.types import Message, CallbackQuery
from typing import Union
from aiogram.filters import BaseFilter

from db.engine import session
from db.models import User


class IsStudent(BaseFilter):
    '''Проверяет id пользователя в базе детей.'''
    PERSONAL = [
        user.id for user in session.query(
            User).filter(User.role != 'kid').all()]

    async def __call__(self, message: Union[Message, CallbackQuery]):
        return message.from_user.id not in self.PERSONAL


class IsMethodist(BaseFilter):
    '''Проверяет id пользователя в базе методистов.'''
    METHODISTS = [
        user.id for user in session.query(
            User).filter(User.role == 'methodist').all()]

    async def __call__(self, message: Union[Message, CallbackQuery]):
        return message.from_user.id in self.METHODISTS


class IsCounselour(BaseFilter):
    '''Проверяет id пользователя в базе вожатых.'''
    COUNSELOURS = [
        user.id for user in session.query(
            User).filter(User.role == 'counselour').all()]

    async def __call__(self, message: Union[Message, CallbackQuery]):
        return message.from_user.id in self.COUNSELOURS

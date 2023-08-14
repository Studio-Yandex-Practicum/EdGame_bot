import logging
from sqlalchemy.orm import sessionmaker, scoped_session

from .engine import engine
from .models import User, Achievement, Artifact, AchievementStatus

logger = logging.getLogger(__name__)
session = scoped_session(sessionmaker(bind=engine()))


class DBManager():
    '''Класс для управления базой данных.'''
    def __init__(self):
        self.session = session

    def create_user(self, id: int, name: str, login: str,
                    password: str = 'any', role: str = 'kid',
                    language: str = 'ru', score: int = 0):
        self.id = id
        self.name = name
        self.login = login
        self.password = password
        self.role = role
        self.language = language
        self.score = score
        try:
            self.session.add(
                User(id=self.id, name=self.name, login=self.login,
                     password=self.password, role=self.role,
                     language=self.language, score=self.score))
            self.session.commit()
            logger.info('Пользователь создан')
        except Exception as err:
            logger.error(f'Ошибка при создании пользователя: {err}')

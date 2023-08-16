from sqlalchemy.exc import IntegrityError

from db.models import User
from db.engine import session


def register_user(message):
    name = message.chat.first_name if message.chat.first_name else None
    user = User(id=int(message.chat.id), name=name, role="kid", language="RU", score=0)

    session.add(user)

    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()  # откатываем session.add(user)
        return False


def select_user(user_id):
    user = session.query(User).filter(User.id == user_id).first()
    return user


def set_user_param(user: User, name: str = None, role: str = None,
                   language: str = None, score: int = None):
    if name:
        user.name = name
    elif role:
        user.role = role
    elif language:
        user.language = language
    elif score:
        user.score = score
    try:
        session.commit()
    except IntegrityError:
        session.rollback()

from sqlalchemy.orm import Session
from db.models import Achievement, AchievementStatus

from db.engine import session


def get_all_achievement(session: Session):
    return session.query(Achievement).all()


def get_achievement_description(session: Session, achievement_id: int) -> str:
    achievemen = session.query(Achievement).filter(Achievement.id 
                                                   == achievement_id).first()
    return achievemen.description


def get_achievement_status(session: Session, achievement_id: int) -> str:
    achievemen = session.query(AchievementStatus).filter(
        AchievementStatus.achievement_id == achievement_id
        ).first()
    return achievemen.status


def get_achievement_type(session: Session, achievement_id: int) -> str:
    achievemen = session.query(Achievement).filter(
                               Achievement.id ==
                               achievement_id).first()
    return achievemen.achievement_type

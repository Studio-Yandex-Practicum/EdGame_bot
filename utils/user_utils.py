from sqlalchemy.orm import Session

from db.models import Achievement, User, AchievementStatus


def get_user_name(session: Session, user_id: int) -> str:
    user = session.query(User).filter(User.id == user_id).first()
    return user.name if user else "Unknown User"


def get_achievement_name(session: Session, achievement_id: int) -> str:
    achievement = (
        session.query(Achievement).filter(Achievement.id == achievement_id).first()
    )
    return achievement.name if achievement else "Unknown Achievement"


def get_achievement_description(session: Session, achievement_id: int) -> str:
    achievement = (
        session.query(Achievement).filter(Achievement.id == achievement_id).first()
    )
    return achievement.description if achievement else "Unknown Achievement"


def get_achievement_instruction(session: Session, achievement_id: int) -> str:
    achievement = (
        session.query(Achievement).filter(Achievement.id == achievement_id).first()
    )
    return achievement.instruction if achievement else "Unknown Achievement"


def get_achievement_image(session: Session, achievement_id: int) -> bytes:
    achievement = (
        session.query(Achievement).filter(Achievement.id == achievement_id).first()
    )
    return achievement.image if achievement else b""


def change_achievement_status_by_id(session: Session, id: int, new_status: str) -> bool:
    if achievement_status := (
        session.query(AchievementStatus).filter(AchievementStatus.id == id).first()
    ):
        achievement_status.status = new_status
        session.commit()
        return True
    return False

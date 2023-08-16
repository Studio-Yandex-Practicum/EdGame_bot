from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import CheckConstraint

from db.engine import engine

DeclarativeBase = declarative_base()


class User(DeclarativeBase):
    __tablename__ = "users"

    id = Column("user_id", Integer, nullable=False, primary_key=True)
    name = Column(String(50), nullable=False)
    role = Column(
        String,
        CheckConstraint(r"role in ('methodist', 'councelor', 'kid')"),
        nullable=False,
    )
    # login = Column(String(50), unique=True, nullable=False)
    # password = Column(String(50), nullable=False)
    language = Column(
        String, CheckConstraint(r"language in ('ru', 'en', 'tt')"), nullable=False
    )
    login = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    language = Column(
        String, CheckConstraint(r"language in ('ru', 'en', 'tt')"), nullable=False
    )
    score = Column("user_score", Integer, nullable=False)

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


class Achievement(DeclarativeBase):
    __tablename__ = "achievements"

    id = Column("achievement_id", Integer, nullable=False, primary_key=True)
    name = Column(String(50), nullable=False)
    image = Column(LargeBinary, nullable=False)
    description = Column(String(255), nullable=False)
    instruction = Column(String(255), nullable=False)
    artifact_type = Column(
        String,
        CheckConstraint(r"artifact_type in ('text', 'image', 'video')"),
        nullable=False,
    )
    achievement_type = Column(
        String,
        CheckConstraint(r"achievement_type in ('individual', 'teamwork')"),
        nullable=False,
    )
    score = Column("achievement_score", Integer, nullable=False)
    price = Column(Integer, nullable=True)

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


class AchievementStatus(DeclarativeBase):
    __tablename__ = "users_achievements"

    id = Column("user_achievement_id", Integer, nullable=False, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    achievement_id = Column(
        Integer,
        ForeignKey("achievements.achievement_id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(
        String,
        CheckConstraint(r"status in ('pending', 'approved', 'rejected')"),
        nullable=False,
    )
    created_at = Column(TIMESTAMP, nullable=False)
    rejection_reason = Column(String(255), nullable=True)

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


class Artifact(DeclarativeBase):
    __tablename__ = "artifacts"

    id = Column("artifact_id", Integer, nullable=False, primary_key=True)
    user_achievement_id = Column(
        Integer,
        ForeignKey("users_achievements.user_achievement_id", ondelete="CASCADE"),
        nullable=False,
    )
    content = Column(LargeBinary, nullable=False)
    artifact_type = Column(
        String,
        CheckConstraint(r"artifact_type in ('text', 'image', 'video')"),
        nullable=False,
    )

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


def create_db():
    # Метод создания таблиц бд по коду сверху
    DeclarativeBase.metadata.create_all(engine())


if __name__ == "__main__":
    create_db()

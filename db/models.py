from sqlalchemy import ARRAY, TIMESTAMP, Column, ForeignKey, Integer, String, \
    BigInteger
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.schema import CheckConstraint

from engine import engine

DeclarativeBase = declarative_base()


class User(DeclarativeBase):
    __tablename__ = "users"

    id = Column("user_id", BigInteger, nullable=False, primary_key=True)
    name = Column(String(50), nullable=False)
    role = Column(
        String,
        CheckConstraint(r"role in ('methodist', 'councelor', 'kid')"),
        nullable=False,
    )
    language = Column(
        String,
        CheckConstraint(r"language in ('RU', 'EN', 'TT')"),
        nullable=False,
    )

    score = Column("user_score", Integer, nullable=False)
    group = Column(Integer, nullable=False)

    team_id = Column(Integer, ForeignKey("team.id", ondelete="SET NULL"))
    team = relationship("Team", back_populates="users")

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


class Achievement(DeclarativeBase):
    __tablename__ = "achievements"

    id = Column("achievement_id", Integer, nullable=False, primary_key=True)
    name = Column(String(50), nullable=False)
    image = Column(String, nullable=False)
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
    price = Column(Integer, nullable=False)

    category_id = Column(
        Integer,
        ForeignKey("category.id", ondelete="SET NULL"))
    category = relationship("Category", back_populates="achievements")

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


class AchievementStatus(DeclarativeBase):
    __tablename__ = "users_achievements"

    id = Column(
        "user_achievement_id", Integer, nullable=False, primary_key=True
    )
    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    achievement_id = Column(
        Integer,
        ForeignKey("achievements.achievement_id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(
        String,
        CheckConstraint(
            r"status in ('pending', 'pending_methodist', 'approved', "
            r"'rejected')"
        ),
        nullable=False,
    )
    files_id = Column(ARRAY(String), nullable=True)
    message_text = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False)
    rejection_reason = Column(String(255), nullable=True)
    user = relationship(
        'User', foreign_keys='AchievementStatus.user_id',
        lazy='joined'
        )
    achievement = relationship(
        'Achievement',
        foreign_keys='AchievementStatus.achievement_id',
        lazy='joined'
        )

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


class Team(DeclarativeBase):
    """Модель для команд. Связь с User."""
    __tablename__ = "team"

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String(50), nullable=False)
    team_size = Column(Integer, nullable=False)
    users = relationship(User, order_by=User.id, back_populates="team")

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


class Category(DeclarativeBase):
    """Модель для категорий. Связь с Achievement."""
    __tablename__ = "category"

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String(50), nullable=False)
    achievements = relationship(
        Achievement,
        order_by=Achievement.id,
        back_populates="category")

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


def create_db():
    # Метод создания таблиц бд по коду сверху
    DeclarativeBase.metadata.create_all(engine)


if __name__ == "__main__":
    create_db()

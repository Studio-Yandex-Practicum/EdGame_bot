from models import Achievement, AchievementStatus, Category, Team, User

from db.engine import session_scope


def delete_test_data(session):
    session.query(AchievementStatus).delete()
    session.query(Achievement).delete()
    session.query(User).delete()
    session.query(Team).delete()
    session.query(Category).delete()


if __name__ == "__main__":
    with session_scope() as session:
        delete_test_data(session)

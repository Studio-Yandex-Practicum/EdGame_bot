from models import Achievement, AchievementStatus, Category, Team, User, engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()


def delete_test_data():
    session.query(AchievementStatus).delete()
    session.query(Achievement).delete()
    session.query(User).delete()
    session.query(Team).delete()
    session.query(Category).delete()

    session.commit()
    session.close()


if __name__ == "__main__":
    delete_test_data()

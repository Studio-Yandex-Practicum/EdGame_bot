from models import Achievement, AchievementStatus, User, engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()


session.query(AchievementStatus).delete()
session.query(Achievement).delete()
session.query(User).delete()

session.commit()
session.close()

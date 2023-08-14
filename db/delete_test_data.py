from models import Achievement, AchievementStatus, Artifact, User, engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

session.query(Artifact).delete()
session.query(AchievementStatus).delete()
session.query(Achievement).delete()
session.query(User).delete()

session.commit()
session.close()

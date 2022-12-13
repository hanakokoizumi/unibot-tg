from sqlalchemy import Column, String, Integer, DateTime, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import os
import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    uid = Column(Integer, index=True)
    server = Column(String(2))
    gid = Column(String(20))
    create_time = Column(DateTime, default=datetime.datetime.now)


if os.path.exists('./data/bot.db'):
    engine = create_engine('sqlite:///data/bot.db', echo=False)
else:
    engine = create_engine('sqlite:///data/bot.db', echo=False)
    Base.metadata.create_all(engine)
sess1 = sessionmaker(bind=engine)
sess = scoped_session(sess1)

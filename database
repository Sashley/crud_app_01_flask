from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models import Base

engine = create_engine('sqlite:///people.db')
db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))

def init_db():
    Base.metadata.create_all(bind=engine)

def shutdown_session(exception=None):
    db_session.remove()

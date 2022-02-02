from sqlalchemy import Column, String, INT, DATETIME, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Sells(Base):

    __tablename__ = 'sells'

    tradeID = Column(INT, primary_key=True)
    tradeValue = Column(INT)
    tradeTime = Column(DATETIME, func.now())



class Buys(Base):

    __tablename__ = 'buys'

    tradeID = Column(INT, primary_key=True)
    tradeValue = Column(INT)
    tradeTime = Column(DATETIME, func.now())


from sqlalchemy import create_engine
engine = create_engine("sqlite:///R2D2_db.sqlite")

from sqlalchemy.orm import sessionmaker
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)



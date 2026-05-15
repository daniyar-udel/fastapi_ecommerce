from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = 'sqlite:///ecommerce.db'

engine = create_engine(DATABASE_URL, echo=True)

Sessionlocal = sessionmaker(engine)

class Base(DeclarativeBase):
    pass

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import DB_CONNECTION


class DatabaseHandler:
    engine = create_engine(DB_CONNECTION)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()

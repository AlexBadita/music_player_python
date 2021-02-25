from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy import Column

# Every models shall inherit this class.
DeclarativeBase = declarative_base()


class BaseModel:
    id = Column(INTEGER, primary_key=True, autoincrement=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
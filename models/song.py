from models import DeclarativeBase, BaseModel
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR
from settings import DB_CONNECTION
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship


class Song(DeclarativeBase, BaseModel):
    __tablename__ = 'songs'
    title = Column(VARCHAR(225), nullable=False, unique=True)
    location = Column(VARCHAR(225), nullable=False, unique=True)
    playlist_item = relationship('PlaylistItem')


if __name__ == '__main__':
    engine = create_engine(DB_CONNECTION)
    DeclarativeBase.metadata.create_all(bind=engine)


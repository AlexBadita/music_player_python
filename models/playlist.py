from models import DeclarativeBase, BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import VARCHAR, INTEGER
from settings import DB_CONNECTION
from sqlalchemy import create_engine
from models.song import Song
from sqlalchemy.orm import relationship


class Playlist(DeclarativeBase, BaseModel):
    __tablename__ = 'playlists'
    playlist_name = Column(VARCHAR(225), nullable=False, unique=True)
    playlist_item = relationship('PlaylistItem')


class PlaylistItem(DeclarativeBase, BaseModel):
    __tablename__ = 'playlists_item'
    song_id = Column(INTEGER, ForeignKey(Song.id))
    song = relationship(Song)
    playlist_id = Column(INTEGER, ForeignKey(Playlist.id))
    playlist = relationship(Playlist)


if __name__ == '__main__':
    engine = create_engine(DB_CONNECTION)
    DeclarativeBase.metadata.create_all(bind=engine)


from datetime import datetime
from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text)
from scrapy.utils.project import get_project_settings

Base = declarative_base()

chapter_team_association_table = Table('ChapterTeam', Base.metadata,
    Column('team_id', ForeignKey('teams.id'), primary_key=True),
    Column('chapter_id', ForeignKey('chapters.id'), primary_key=True)
)

manga_team_association_table = Table('MangaTeam', Base.metadata,
    Column('team_id', ForeignKey('teams.id'), primary_key=True),
    Column('manga_id', ForeignKey('mangas.id'), primary_key=True)
)

def db_connect(connection_string):
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    print(connection_string)
    return create_engine(connection_string)


def create_table(engine):
    Base.metadata.create_all(engine)


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column('name', String(50), unique=True)
    langage = Column('team', String(50))
    url = Column('url', String(150))
    # Has many chapters
    mangas = relationship("Manga",
                          secondary=manga_team_association_table,
                          back_populates='teams')
    # Has many chapters
    chapters = relationship("Chapter",
                            secondary=chapter_team_association_table,
                            back_populates='teams')
    
    

class Manga(Base):
    __tablename__ = "mangas"

    id = Column(Integer, primary_key=True)
    title = Column('title', String(50), unique=True)
    url = Column('url', String(150))
    cover_checksum = Column('cover_checksum', String(150))
    cover_path = Column('cover_path', String(150))
    cover_url = Column('cover_url', String(150))
    # Has many chapters
    chapters = relationship('Chapter', back_populates='manga')
    # Belongs to many teams
    teams = relationship("Team",
                         secondary=manga_team_association_table,
                         back_populates='mangas')


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True)
    number = Column('number', Float)
    title = Column('title', String(150))
    url = Column('url', String(150))
    date = Column('date', DateTime)
    # Belongs to one manga
    manga_id = Column(Integer, ForeignKey('mangas.id'), nullable=False, index=True)
    manga = relationship('Manga', back_populates='chapters')
    # Belongs to many teams
    teams = relationship("Team",
                         secondary=chapter_team_association_table,
                         back_populates='chapters')
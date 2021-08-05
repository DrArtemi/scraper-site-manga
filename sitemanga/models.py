from datetime import datetime
from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text)
from scrapy.utils.project import get_project_settings

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    print(get_project_settings().get("CONNECTION_STRING"))
    return create_engine(get_project_settings().get("CONNECTION_STRING"))


def create_table(engine):
    Base.metadata.create_all(engine)


class Manga(Base):
    __tablename__ = "mangas"

    id = Column(Integer, primary_key=True)
    title = Column('title', String(50), unique=True)
    team = Column('team', String(50))
    cover_checksum = Column('cover_checksum', String(150))
    cover_path = Column('cover_path', String(150))
    cover_url = Column('cover_url', String(150))


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True)
    number = Column('number', String(50))
    title = Column('title', String(150))
    url = Column('url', String(150))
    date = Column('date', DateTime)
    manga_id = Column(Integer, ForeignKey('mangas.id'), nullable=False, index=True)
    manga = relationship('Manga', backref='chapters', foreign_keys=[manga_id])
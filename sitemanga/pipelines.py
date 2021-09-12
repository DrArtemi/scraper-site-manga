# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.functions import func
from sitemanga.models import Manga, Chapter, Team, db_connect, create_table

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class StorePipeline(object):
    def __init__(self, connection_string):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        engine = db_connect(connection_string)
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        connection_string = settings.get("CONNECTION_STRING")
        return cls(connection_string)


    def process_item(self, item, spider):
        """Save quotes in the database
        This method is called for every item pipeline component
        """
        item_dict = ItemAdapter(item).asdict()        
        session = self.Session()
        
        # TEAM
        exist_team = session.query(Team).filter_by(
            name=item['team_name'],
            url=item['team_url']
        ).first()
        team = exist_team if exist_team is not None else Team()
        
        if exist_team is None:        
            team.name = item['team_name']
            team.langage = item['team_langage']
            team.url = item['team_url']
        
        # MANGA
        exist_manga = session.query(Manga).filter(
            func.lower(Manga.title) == func.lower(item['manga_title'])
        ).first()
        
        manga = exist_manga if exist_manga is not None else Manga()
        
        if exist_manga is not None:
            if item['manga_url'] not in manga.url:
                manga.url += ';' + item['manga_url']
        else:
            manga.title = item['manga_title']
            manga.url = item['manga_url']
        
        manga.cover_checksum = item['images'][0]['checksum'] if len(item['images']) > 0 else ''
        manga.cover_path = item['images'][0]['path'] if len(item['images']) > 0 else ''
        manga.cover_url = item['images'][0]['url'] if len(item['images']) > 0 else ''
        manga.teams.append(team)
        
        # CHAPTER
        exist_chapter = session.query(Chapter).filter_by(
            manga_id=manga.id if exist_manga is not None else 0,
            number=item['chapter_number']
        ).first()
        chapter = exist_chapter if exist_chapter is not None else Chapter()

        chapter.manga = manga
        if exist_chapter is not None:
            if item['chapter_url'] not in chapter.url:
                chapter.url += ';' + item['chapter_url']
        else:
            chapter.number = item['chapter_number']
            chapter.url = item['chapter_url']
            chapter.title = item['chapter_title']
        chapter.date = item['chapter_date']
        chapter.teams.append(team)
        
        try:
            session.add(chapter)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
            
        return item

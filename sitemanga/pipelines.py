# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem
from sqlalchemy.sql.functions import func
from sitemanga.models import Manga, Chapter, db_connect, create_table


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
        
        # Check whether the manga exists
        exist_manga = session.query(Manga).filter(
            func.lower(Manga.title) == func.lower(item_dict['manga_title'])
        ).first()
        exist_chapter = session.query(Chapter).filter_by(
            manga_id=exist_manga.id if exist_manga is not None else 0,
            number=item_dict['chapter_number']
        ).first()
        
        manga = exist_manga if exist_manga is not None else Manga()
        chapter = exist_chapter if exist_chapter is not None else Chapter()
        
        # Manga infos
        if exist_manga is not None:
            if item_dict['manga_team'] not in manga.team:
                manga.team += ';' + item_dict['manga_team']
            if item_dict['manga_url'] not in manga.url:
                manga.url += ';' + item_dict['manga_url']
        else:
            manga.title = item_dict['manga_title']
            manga.team = item_dict['manga_team']
            manga.url = item_dict['manga_url']
        
            manga.cover_checksum = item_dict['images'][0]['checksum'] if len(item_dict['images']) > 0 else ''
            manga.cover_path = item_dict['images'][0]['path'] if len(item_dict['images']) > 0 else ''
            manga.cover_url = item_dict['images'][0]['url'] if len(item_dict['images']) > 0 else ''
        
        chapter.manga = manga
        
        # Chapter infos
        if exist_chapter is not None:
            if item_dict['chapter_url'] not in chapter.url:
                chapter.url += ';' + item_dict['chapter_url']
        else:
            chapter.number = item_dict['chapter_number']
            chapter.url = item_dict['chapter_url']
            chapter.date = item_dict['chapter_date']
            chapter.title = item_dict['chapter_title']
                
        try:
            session.add(chapter)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
                        
        return item

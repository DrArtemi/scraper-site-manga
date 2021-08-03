# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem
from sitemanga.models import Manga, Chapter, db_connect, create_table


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
        

class StorePipeline(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
    
    def process_item(self, item, spider):
        """Save quotes in the database
        This method is called for every item pipeline component
        """
        item_dict = ItemAdapter(item).asdict()
        
        session = self.Session()
        
        manga = Manga()
        chapter = Chapter()
        
        # Check whether the manga exists
        exist_manga = session.query(Manga).filter_by(title=item_dict['manga_title'], team=item_dict['manga_team']).first()
        exist_chapter = session.query(Chapter).filter_by(url=item_dict['chapter_url']).first()
        
        # Manga infos
        manga.title = item_dict['manga_title']
        manga.team = item_dict['manga_team']
        
        manga.cover_checksum = item_dict['images'][0]['checksum'] if len(item_dict['images']) > 0 else ''
        manga.cover_path = item_dict['images'][0]['path'] if len(item_dict['images']) > 0 else ''
        manga.cover_url = item_dict['images'][0]['url'] if len(item_dict['images']) > 0 else ''
        
        chapter.manga = exist_manga if exist_manga is not None else manga
        
        # Chapter infos
        chapter.number = item_dict['chapter_number']
        chapter.url = item_dict['chapter_url']
        chapter.date = item_dict['chapter_date']
        chapter.title = item_dict['chapter_title']
                
        if exist_chapter is None:
            try:
                session.add(chapter)
                session.commit()
            except:
                session.rollback()
                raise
            finally:
                session.close()
        else:
            session.rollback()
            session.close()
            
        return item

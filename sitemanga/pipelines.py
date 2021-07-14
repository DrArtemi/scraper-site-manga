# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from sitemanga.items import ChapterItem, MangaItem
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
    
    def store_manga(self, item, spider):
        session = self.Session()
        manga = Manga()
        
        # Infos
        manga.title = item['title']
        manga.team = item['team']
        # Image
        manga.cover_checksum = item['images'][0]['checksum'] if len(item['images']) > 0 else ''
        manga.cover_path = item['images'][0]['path'] if len(item['images']) > 0 else ''
        manga.cover_url = item['images'][0]['url'] if len(item['images']) > 0 else ''
        
        # check whether the manga exists
        exist_manga = session.query(Manga).filter_by(title=manga.title, team=manga.team).first()
        
        if exist_manga is None:
            try:
                session.add(manga)
                session.commit()
            except:
                session.rollback()
                raise
            finally:
                session.close()

        return item
        
    
    def store_chapter(self, item, spider):
        session = self.Session()
        chapter = Chapter()
        
        # Infos
        chapter.number = item['number']
        chapter.url = item['url']
        chapter.date = item['date']
        chapter.title = item['title']
        
        # check whether the manga exists
        exist_manga = session.query(Manga).filter_by(title=item['manga'], team=item['team']).first()
        
        if exist_manga is not None:
            chapter.manga = exist_manga
            exist_chapter = session.query(Chapter).filter_by(url=chapter.url).first()
            
            if exist_chapter is None:
                try:
                    session.add(chapter)
                    session.commit()
                except:
                    session.rollback()
                    raise
                finally:
                    session.close()
        
        return item

    def process_item(self, item, spider):
        """Save quotes in the database
        This method is called for every item pipeline component
        """
        item_dict = ItemAdapter(item).asdict()
        
        if isinstance(item, MangaItem):
            return self.store_manga(item_dict, spider)
        elif isinstance(item, ChapterItem):
            return self.store_chapter(item_dict, spider)
        
        return item

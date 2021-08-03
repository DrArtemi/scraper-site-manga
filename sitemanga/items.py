# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ChapterItem(scrapy.Item):
    # Manga infos
    manga_title = scrapy.Field()
    manga_team = scrapy.Field()
    # Manga cover
    image_urls = scrapy.Field()
    images = scrapy.Field()
    
    # Chapter infos
    chapter_number = scrapy.Field()
    chapter_url = scrapy.Field()
    chapter_date = scrapy.Field()
    chapter_title = scrapy.Field()

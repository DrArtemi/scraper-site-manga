# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScanItem(scrapy.Item):
    # TEAM
    team_name = scrapy.Field()
    team_langage = scrapy.Field()
    team_url = scrapy.Field()
    
    # MANGA
    manga_title = scrapy.Field()
    manga_url = scrapy.Field()
    # Manga cover
    image_urls = scrapy.Field()
    images = scrapy.Field()
    
    # CHAPTER
    chapter_number = scrapy.Field()
    chapter_url = scrapy.Field()
    chapter_date = scrapy.Field()
    chapter_title = scrapy.Field()

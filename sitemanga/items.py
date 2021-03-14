# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MangaItem(scrapy.Item):
    title = scrapy.Field()
    cover = scrapy.Field()
    

class ChapterItem(scrapy.Item):
    manga = scrapy.Field()
    number = scrapy.Field()
    url = scrapy.Field()
    date = scrapy.Field()
    title = scrapy.Field()

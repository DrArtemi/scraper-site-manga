from sitemanga.spiders.utils import equalize_similar_dates
from sitemanga.items import ChapterItem
import scrapy
import dateparser
from urllib.parse import urljoin



class ScantradSpider(scrapy.Spider):
    name = "scantrad"
    team_name = "Scantrad France"
    base_url = "https://scantrad.net/"
    
    def start_requests(self):
        urls = [
            'https://scantrad.net/mangas',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_main_page)

    def parse_main_page(self, response):
        print(f'Parsing mangas list at {response.url}')
        
        mangas_urls = response.css('div.manga .manga_right a::attr(href)').getall()
        for i in range(len(mangas_urls)):
            mangas_urls[i] = urljoin(self.base_url, mangas_urls[i])
        
        for url in mangas_urls:
            yield scrapy.Request(url=url, callback=self.parse_manga)

    def parse_manga(self, response):
        print(f'Parsing manga at {response.url}')
        manga_infos = {}
        
        manga_infos['title'] = response.css('.info .titre::text').get()
        manga_infos['cover'] = response.css('.ctt-img img::attr(src)').get()
                
        chapters = response.css('.chapitre')
    
        manga_infos['chapters'] = [{
                'number': ch.css('span.chl-num::text').get().split(' ')[1],
                'url': urljoin(self.base_url, ch.css('a.hm-link::attr(href)').get()),
                'title': ch.css('span.chl-titre::text').get(),
                'date': dateparser.parse(ch.css('div.chl-date::text').get())
            } for ch in chapters]
        # Needed if date is similar to put chapters in the right order.
        equalize_similar_dates(manga_infos['chapters'], threshold=1)
        
        for info in manga_infos['chapters']:
            yield ChapterItem(
                manga_title=manga_infos['title'],
                manga_team=self.team_name,
                manga_url=response.url,
                image_urls=[manga_infos['cover']],
                chapter_number=int(info['number']),
                chapter_url=info['url'],
                chapter_date=info['date'],
                chapter_title=info['title'],
            )
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
        
        mangas_urls = response.css('a.home-manga::attr(href)').getall()
        for i in range(len(mangas_urls)):
            mangas_urls[i] = urljoin(self.base_url, mangas_urls[i])
        
        for url in mangas_urls:
            yield scrapy.Request(url=url, callback=self.parse_manga)

    def parse_manga(self, response):
        print(f'Parsing manga at {response.url}')
        manga_infos = {}
        
        manga_infos['title'] = response.css('.mf-info .titre::text').get()
        manga_infos['cover'] = response.css('.poster img::attr(src)').get()
                
        chapters = response.css('.chapitre')
        real_chapters = [ch for ch in chapters if len(ch.css('.chl-num')) > 0]
    
        manga_infos['chapters'] = [{
                'number': ch.css('span.chl-num::text').get().replace('#', ''),
                'url': urljoin(self.base_url, ch.css('a.chr-button::attr(href)').get()),
                'title': ch.css('span.chl-titre::text').get(),
                'date': dateparser.parse(ch.css('div.chl-date::text').get())
            } for ch in real_chapters]
        
        for info in manga_infos['chapters']:
            yield ChapterItem(
                manga=manga_infos['title'],
                number=info['number'],
                url=info['url'],
                date=info['date'],
                title=info['title'],
            )
from sitemanga.items import ScanItem
from sitemanga.spiders.utils import equalize_similar_dates
import scrapy
import dateparser
from urllib.parse import urljoin



class ScantradSpider(scrapy.Spider):
    name = "scantrad"
    
    team = {
        'name': 'Scantrad France',
        'langage': 'fr',
        'url': 'https://scantrad.net/'
    }
    
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
            mangas_urls[i] = urljoin(self.team['url'], mangas_urls[i])
        
        for url in mangas_urls:
            yield scrapy.Request(url=url, callback=self.parse_manga)

    def parse_manga(self, response):
        print(f'Parsing manga at {response.url}')
        
        manga_title = response.css('.info .titre::text').get()
        manga_cover = response.css('.ctt-img img::attr(src)').get()
                
        chapters = response.css('.chapitre')
    
        chapters = [{
                'number': ch.css('span.chl-num::text').get().split(' ')[1],
                'url': urljoin(self.team['url'], ch.css('a.hm-link::attr(href)').get()),
                'title': ch.css('span.chl-titre::text').get(),
                'date': dateparser.parse(ch.css('div.chl-date::text').get(), languages=['fr'])
            } for ch in chapters]
        # Needed if date is similar to put chapters in the right order.
        chapters = equalize_similar_dates(chapters, threshold=1)
        
        for info in chapters:
            yield ScanItem(
                # TEAM
                team_name=self.team['name'],
                team_langage=self.team['langage'],
                team_url=self.team['url'],
                # MANGA
                manga_title=manga_title,
                manga_url=response.url,
                image_urls=[manga_cover],
                # CHAPTER
                chapter_number=info['number'],
                chapter_url=info['url'],
                chapter_date=info['date'],
                chapter_title=info['title'],
            )
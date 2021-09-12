from sitemanga.items import ScanItem
from sitemanga.spiders.utils import equalize_similar_dates
import scrapy
import dateparser
from urllib.parse import urljoin


class ReaperscansfrSpider(scrapy.Spider):
    name = "zeroscans"

    team = {
        'name': 'Zero Scans',
        'langage': 'us',
        'url': 'https://zeroscans.com/'
    }


    def start_requests(self):
        urls = [
            'https://zeroscans.com/comics?page=1',
            'https://zeroscans.com/comics?page=2',
            'https://zeroscans.com/comics?page=3',
            'https://zeroscans.com/comics?page=4'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_main_page)

    def parse_main_page(self, response):
        print(f'Parsing mangas list at {response.url}')
        
        mangas_links = response.css('.list-item .media-comic-card a.media-content::attr(href)').getall()
        
        for link in mangas_links:
            yield scrapy.Request(url=link, callback=self.parse_manga)
    
    def parse_manga(self, response):
        print(f'Parsing manga at {response.url}')
        manga_title = response.css('.d-flex .heading h5::text').get().strip()
        manga_cover = response.css('.media-comic-card a::attr(style)').get()
        manga_cover = urljoin(self.team["url"], manga_cover.replace('background-image:url(', '').replace(')', ''))
                        
        # Chapters
        chapters_number = response.css('.list .list-item span::text').getall()
        chapters_url = response.css('.list .list-item a.item-author::attr(href)').getall()
        chapters_title = response.css('.list .list-item a.item-author::text').getall()
        chapters_date = response.css('.list .list-item a.item-company::text').getall()
                                
        chapters = [{
                'number': chapters_number[i].strip(),
                'url': chapters_url[i],
                'title': chapters_title[i].strip(),
                'date': dateparser.parse(chapters_date[i], languages=['en'])
            } for i in range(len(chapters_number))]
                
        # # Needed if date is similar to put chapters in the right order.
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

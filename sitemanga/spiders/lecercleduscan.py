from sitemanga.items import ScanItem
from sitemanga.spiders.utils import equalize_similar_dates
import scrapy
import dateparser


class LecercleduscanSpider(scrapy.Spider):
    name = "lecercleduscan"
    
    team = {
        'name': 'Le cercle du scan',
        'langage': 'fr',
        'url': 'http://www.lecercleduscan.com/'
    }

    def start_requests(self):
        urls = [
            'http://www.lecercleduscan.com/projets/manga/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_main_page)

    def parse_main_page(self, response):
        print(f'Parsing mangas list at {response.url}')
        
        mangas_links = response.css('.project-item a::attr(href)').getall()
        
        for link in mangas_links:
            yield scrapy.Request(url=link, callback=self.parse_manga)
    
    def parse_manga(self, response):
        print(f'Parsing manga at {response.url}')
        manga_infos = {}
        
        manga_title = response.css('.zone-page h2::text').get()
        manga_cover = response.css('.zone-page img::attr(src)').get()
                        
        # Chapters
        chapters_url = response.css('.list-group a.list-group-item::attr(href)').getall()
        chapters_title = response.css('.list-group a.list-group-item::text').getall()
        chapters_date = response.css('.list-group a.list-group-item span::text').getall()
        chapters_number = [0 for _ in range(len(chapters_url))]
        
        # Clean dates
        for i in range(len(chapters_url)):
            chapters_date[i] = ' '.join(chapters_date[i].split())
            title_list = chapters_title[i].split(' - ')
            chapters_title[i] = title_list[2].strip() if len(title_list) > 2 else ''
            chapter_splitted = title_list[1].split('°')
            chapters_number[i] = chapter_splitted[1] if len(chapter_splitted) > 1 else chapters_number[i]
                
        chapters = [{
                'number': chapters_number[i],
                'url': chapters_url[i],
                'title': chapters_title[i],
                'date': dateparser.parse(chapters_date[i], languages=['fr'])
            } for i in range(len(chapters_number))]
        
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

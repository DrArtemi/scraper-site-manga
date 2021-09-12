from sitemanga.spiders.utils import equalize_similar_dates
from sitemanga.items import ScanItem
import scrapy
import dateparser


class FuryosquadSpider(scrapy.Spider):
    name = "furyosquad"
    
    team = {
        'name': 'FuryoSquad',
        'langage': 'fr',
        'url': 'https://furyosquad.com'
    }

    def start_requests(self):
        urls = [
            'https://furyosquad.com/mangas',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_main_page)

    def parse_main_page(self, response):
        print(f'Parsing mangas list at {response.url}')
        
        mangas_links = response.css('.fs-comic-title a::attr(href)').getall()
        
        for link in mangas_links:
            yield scrapy.Request(url=link, callback=self.parse_manga)
    
    def parse_manga(self, response):
        print(f'Parsing manga at {response.url}')
        
        # Manga
        manga_title = response.css('.fs-comic-title::text').get()
        manga_cover = response.css('.comic-cover::attr(src)').get()
                        
        # Chapters
        chapters_number = response.css('.fs-chapter-list .element.desktop .title a::text').getall()
        chapters_url = response.css('.fs-chapter-list .element.desktop .title a::attr(href)').getall()
        chapters_title = response.css('.fs-chapter-list .element.desktop .name::text').getall()
        chapters_date = response.css('.fs-chapter-list .element.desktop .meta_r::text').getall()
        
        for i, ch in enumerate(chapters_number):
            splitted = ch.split(' ')
            chapters_number[i] = float(splitted[1]) if len(splitted) > 1 else float(ch)
        
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

from sitemanga.items import ChapterItem, MangaItem
import scrapy
import dateparser


class FuryosquadSpider(scrapy.Spider):
    name = "furyosquad"

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
        manga_infos = {}
        
        manga_infos['title'] = response.css('.fs-comic-title::text').get()
        manga_infos['cover'] = response.css('.comic-cover::attr(src)').get()
        
        yield MangaItem(
            title=manga_infos['title'],
            cover=manga_infos['cover']
        )
                
        # Chapters
        chapters_number = response.css('.fs-chapter-list .element .title a::text').getall()
        chapters_url = response.css('.fs-chapter-list .element .title a::attr(href)').getall()
        chapters_title = response.css('.fs-chapter-list .element .name::text').getall()
        chapters_date = response.css('.fs-chapter-list .element .meta_r::text').getall()
        
        for i, ch in enumerate(chapters_number):
            splitted = ch.split(' ')
            chapters_number[i] = splitted[1] if len(splitted) > 1 else ch
        
        manga_infos['chapters'] = [{
                'number': chapters_number[i],
                'url': chapters_url[i],
                'title': chapters_title[i],
                'date': dateparser.parse(chapters_date[i])
            } for i in range(len(chapters_number))]
        
        for info in manga_infos['chapters']:
            yield ChapterItem(
                manga=manga_infos['title'],
                number=info['number'],
                url=info['url'],
                date=info['title'],
                title=info['date'],
            )
            

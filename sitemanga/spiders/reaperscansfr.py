from sitemanga.spiders.utils import equalize_similar_dates
import scrapy
import dateparser


class ReaperscansfrSpider(scrapy.Spider):
    name = "reaperscansfr"
    team_name = "Reaper Scan Fr"


    def start_requests(self):
        urls = [
            'https://reaperscans.fr/manga/?page=1',
            'https://reaperscans.fr/manga/?page=2',
            'https://reaperscans.fr/manga/?page=3'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_main_page)

    def parse_main_page(self, response):
        print(f'Parsing mangas list at {response.url}')
        
        mangas_links = response.css('.listupd .bs a::attr(href)').getall()
        
        for link in mangas_links:
            yield scrapy.Request(url=link, callback=self.parse_manga)
    
    def parse_manga(self, response):
        print(f'Parsing manga at {response.url}')
        manga_infos = {}
        
        manga_infos['title'] = response.css('h1.entry-title::text').get()
        manga_infos['cover'] = response.css('.thumb img::attr(src)').get()
                        
        # Chapters
        chapters_number = response.css('#chapterlist li .chapternum::text').getall()
        chapters_url = response.css('#chapterlist li a::attr(href)').getall()
        chapters_date = response.css('#chapterlist li .chapterdate::text').getall()
        
        for i, ch in enumerate(chapters_number):
            splitted = ch.split(' ')
            chapters_number[i] = splitted[1] if len(splitted) > 1 else ch
                
        manga_infos['chapters'] = [{
                'number': chapters_number[i],
                'url': chapters_url[i],
                'title': '',
                'date': dateparser.parse(chapters_date[i], languages=['fr'])
            } for i in range(len(chapters_number))]
                
        # Needed if date is similar to put chapters in the right order.
        manga_infos['chapters'] = equalize_similar_dates(manga_infos['chapters'], threshold=1)
        
        for i, info in enumerate(manga_infos['chapters']):
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

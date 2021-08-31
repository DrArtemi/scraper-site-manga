from sitemanga.spiders.utils import equalize_similar_dates
import scrapy
import dateparser


class ScantradunionSpider(scrapy.Spider):
    name = "scantradunion"
    team_name = "Scantrad Union"


    def start_requests(self):
        urls = [
            'https://scantrad-union.com/projets/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_main_page)

    def parse_main_page(self, response):
        print(f'Parsing mangas list at {response.url}')
        
        mangas_links = response.css('#main a.index-top3-a::attr(href)').getall()
        
        for link in mangas_links:
            yield scrapy.Request(url=link, callback=self.parse_manga)
    
    def parse_manga(self, response):
        print(f'Parsing manga at {response.url}')
        manga_infos = {}
        
        manga_infos['title'] = response.css('.projet-description h2::text').get()
        manga_infos['cover'] = response.css('.projet-image img::attr(src)').get()
                        
        # # Chapters
        chapters_number = response.css('.links-projects li .chapter-number::text').getall()
        chapters_url = response.css('.links-projects li a.btnlel[href*="scantrad-union"]::attr(href)').getall()
        chapters_title = response.css('.links-projects li .chapter-name::text').getall()
        chapters_date = response.css('.links-projects li .name-chapter span:last-of-type::text').getall()
        
        for i in range(len(chapters_url)):
            chapters_number[i] = chapters_number[i].replace('#', '')
                
        manga_infos['chapters'] = [{
                'number': chapters_number[i],
                'url': chapters_url[i],
                'title': chapters_title[i],
                'date': dateparser.parse(chapters_date[i], languages=['fr'])
            } for i in range(len(chapters_number))]
        
        # # Needed if date is similar to put chapters in the right order.
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

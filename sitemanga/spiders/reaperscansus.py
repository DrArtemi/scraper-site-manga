from sitemanga.items import ScanItem
from sitemanga.spiders.utils import equalize_similar_dates
import scrapy
import dateparser


class ReaperscansfrSpider(scrapy.Spider):
    name = "reaperscansus"

    team = {
        'name': 'Reaper Scan US',
        'langage': 'us',
        'url': 'https://reaperscans.com/'
    }


    def start_requests(self):
        url = 'https://reaperscans.com/wp-admin/admin-ajax.php'
        yield scrapy.FormRequest(
            url=url,
            formdata={
                "action": "madara_load_more",
                "page": "0",
                "template": "madara-core/content/content-archive",
                "vars[orderby]": "meta_value_num",
                "vars[paged]": "0",
                "vars[timerange]": "",
                "vars[posts_per_page]": "500",
                "vars[tax_query][relation]": "OR",
                "vars[meta_query][0][0][key]": "_wp_manga_chapter_type",
                "vars[meta_query][0][0][value]": "manga",
                "vars[meta_query][0][relation]": "AND",
                "vars[meta_query][relation]": "OR",
                "vars[post_type]": "wp-manga",
                "vars[post_status]": "publish",
                "vars[meta_key]": "_wp_manga_views",
                "vars[sidebar]": "right",
                "vars[manga_archives_item_layout]": "big_thumbnail"
            },
            callback=self.parse_main_page)

    def parse_main_page(self, response):
        print(f'Parsing mangas list at {response.url}')
        
        # print(response.body)
        
        mangas_links = response.css('.page-listing-item .item-thumb a::attr(href)').getall()
        
        for link in mangas_links:
            yield scrapy.Request(url=link, callback=self.parse_manga)
    
    def parse_manga(self, response):
        print(f'Parsing manga at {response.url}')        
        manga_title = response.css('.post-title h1::text').get()
        manga_cover = response.css('.summary_image img::attr(data-src)').get()
                        
        # Chapters
        chapters_number = response.css('li.wp-manga-chapter a::text').getall()
        chapters_url = response.css('li.wp-manga-chapter a::attr(href)').getall()
        chapters_date = response.css('li.wp-manga-chapter .chapter-release-date i::text').getall()
        
        for i, ch in enumerate(chapters_number):
            chapters_number[i] = ch.strip()
        chapters_number = list(filter(None, chapters_number))
                
        for i, ch in enumerate(chapters_number):
            splitted = ch.split(' ')
            chapters_number[i] = splitted[1] if len(splitted) > 1 else ch
                
        chapters = [{
                'number': chapters_number[i],
                'url': chapters_url[i],
                'title': '',
                'date': dateparser.parse(chapters_date[i], languages=['en'])
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

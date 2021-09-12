# scraper-site-manga
This repository scrap informations from manga teams websites to feed https://fuckjapscan.com/ website.

## Project setup
`conda env create -f environment.yml`

### Setup your databse
Add this lines to scrapy settings
#### Database
`CONNECTION_STRING = 'sqlite:////path/to/database/fuckjapscan.db'`
#### Image folder
`IMAGES_STORE = '/path/to/images/'`

## Run specific spider
`scrapy crawl spider_name`

For example if you want to run FuryoSquad spider :<br>
`scrapy crawl furyosquad`

## Run all spiders
`scrapyd-deploy` to update egg.<br>
`scrapyd-client schedule -p sitemanga \*` to run spiders.

from typing import Iterable
from urllib.parse import urljoin

import scrapy

from logo.items import BrandsoftheworldItem

class BrandsoftheworldSpiderSpider(scrapy.Spider):
    name = "brandsoftheworld_spider"
    allowed_domains = ["www.brandsoftheworld.com"]

    def __init__(self):
        super().__init__()
        self.domain_url = "https://www.brandsoftheworld.com"
        self.info_key_map = {
            'Website': 'website',
            'Designer': 'designer',
            'Contributor': 'contributor',
            'Vector format': 'vector_format',
            'Status': 'status',
            'Vector Quality': 'vector_quality',
            'Updated on': 'updated_on'
        }

    def start_requests(self):
        start_url = "https://www.brandsoftheworld.com/logos"
        yield scrapy.Request(url=start_url, callback=self.parse_list_page)

    def parse_list_page(self, response):
        # Discover all logos on page
        logos = response.css('ul.logos li')
        for logo in logos:
            logo_link = logo.css('a::attr(href)').get()
            logo_link = urljoin(self.domain_url, logo_link)
            yield scrapy.Request(url=logo_link, callback=self.parse_logo_page)

        # Go to next page
        next_page_link = response.css('li.pager-next a::attr(href)').get()
        if next_page_link is not None:
            next_page_link = urljoin(self.domain_url, next_page_link)
            yield scrapy.Request(url=next_page_link, callback=self.parse_list_page)
        
    def parse_logo_page(self, response):
        term_urls = response.css('div.terms a::attr(href)').getall()
        term_texts = response.css('div.terms a::text').getall()
        terms = [(url, text) for (url, text) in zip (term_urls, term_texts)]
        logo_image_link = response.css('div.image a::attr(href)').get()
        yield scrapy.Request(url=logo_image_link, callback=self.parse_logo_image_link, meta={'terms': terms})

    def parse_logo_image_link(self, response):
        logo_item = BrandsoftheworldItem()

        logo_item['title'] = response.css('h1.clearfix span::text').get()
        logo_item['description'] = response.css('div.desc p::text').getall()
        logo_item['terms'] = response.meta['terms']
        info_keys = response.css('dt::text').getall()
        info_values = response.css('dd::text').getall()
        for (k, v) in zip(info_keys, info_values):
            k = k.replace(':', '')
            logo_item[self.info_key_map[k]] = v
        logo_item['image_urls'] = response.css('div.image img.image::attr(src)').getall()

        yield logo_item
        
        
        



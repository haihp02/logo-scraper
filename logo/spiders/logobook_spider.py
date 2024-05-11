from typing import Iterable
import scrapy

from logo.items import LogobookItem

class LogobookSpiderSpider(scrapy.Spider):
    name = "logobook_spider"
    allowed_domains = ["www.logobook.com"]

    def __init__(self):
        super().__init__()
        self.domain_url = "http://www.logobook.com/"

    def start_requests(self):
        start_url = "http://www.logobook.com/"
        yield scrapy.Request(url=start_url, callback=self.parse_home_page)

    def parse_home_page(self, response):
        # Get all logo classes
        all_logo_class_urls = response.css('section.homepage-logos.m-hide a.logo::attr(href)').getall()
        for logo_class_url in all_logo_class_urls:
            yield scrapy.Request(url=logo_class_url, callback=self.parse_list_page)

    def parse_list_page(self, response):
        # Get all logos in page
        all_logos = response.css('a.logo-block')
        for logo in all_logos:
            if logo.css('figure').get() is None:
                continue
            logo_url = logo.css('::attr(href)').get()
            yield scrapy.Request(url=logo_url, callback=self.parse_logo_page)
        
        # Go to next page
        next_page_link = response.css('nav a.next::attr(href)').get()
        if next_page_link is not None:
            yield scrapy.Request(url=next_page_link, callback=self.parse_list_page)

    def parse_logo_page(self, response):
        logo_item = LogobookItem()

        logo_item['title'] = response.css('div.single-logo-details h2::text').get().strip()
        logo_item['country'] = response.css('div.single-logo-details h3 a::text').get()

        all_info_keys = response.css('div.single-logo-details h4::text').getall()
        all_info_values = response.css('div.single-logo-details h3 a::text').getall()[1:]
        logo_item['infos'] = {}
        for k, v in zip(all_info_keys, all_info_values):
            logo_item['infos'][k.strip()] = v.strip()
        
        logo_item['image_url'] = response.css('section.single-logo figure.logo-svg img.logo::attr(src)').get()
        logo_item['tags'] = list(map(lambda x: x.strip(), response.css('div.single-tags a::text').getall()))

        yield logo_item



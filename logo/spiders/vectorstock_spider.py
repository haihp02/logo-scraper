import sys
import asyncio
import unicodedata
from urllib.parse import urljoin

import scrapy
import scrapy.http
import scrapy.http.request
from scrapy.selector import Selector
import requests
from scrapy_playwright.page import PageMethod

from logo.items import VectorStockItem


class VectorstockSpiderSpider(scrapy.Spider):
    name = "vectorstock_spider"
    allowed_domains = ["www.vectorstock.com"]

    def __init__(self, designer=None, page_num=None, backward=False, watermark=False):
        super().__init__()
        self.domain_url = "https://www.vectorstock.com"
        self.designer = designer
        self.page_num = page_num
        self.backward = bool(backward)
        self.watermark = bool(watermark)

    def start_requests(self):
        if self.designer == None:
            self.start_url = "https://www.vectorstock.com/royalty-free-vectors/logo-vectors-order_isolated"
        else:
            self.start_url = f"https://www.vectorstock.com/royalty-free-vectors/logo-vectors-by_{self.designer.lower()}-order_isolated"
        if self.page_num is not None:
            self.start_url += f'-page_{self.page_num}'
            return scrapy.Request(url=self.start_url, callback=self.parse_list_page, meta={'page': self.page_num})
        else:
            html_content = requests.get(self.start_url).text
            selector = Selector(text=html_content)
            self.max_page_num = int(selector.css('nav.controls div.display input::attr(max)').get())
            self.min_page_num = int(selector.css('nav.controls div.display input::attr(min)').get())
            if not self.backward:
                yield scrapy.Request(url=self.start_url + f'-page_{self.min_page_num}', callback=self.parse_list_page, meta={'page': self.min_page_num})
            else:
                yield scrapy.Request(url=self.start_url + f'-page_{self.max_page_num}', callback=self.parse_list_page, meta={'page': self.max_page_num})
    
    def parse_list_page(self, response):
        if response.meta['page'] > self.max_page_num or response.meta['page'] < self.min_page_num:
            return
        # Discover all logos on page
        logos = response.css("div figure")
        for logo in logos:
            logo_link = logo.css('div.inner a::attr(href)').get()
            # if water mark, get logo image from list page
            if self.watermark:
                image_url = logo.css('source')[0].css('::attr(srcset)').get().split(',')[0].split()[0]
                yield scrapy.Request(url=logo_link, callback=self.parse_logo_page, meta={'image_url': image_url, 'page': response.meta['page']})
            else:
                yield scrapy.Request(url=logo_link, callback=self.parse_logo_page, meta={'page': response.meta['page']})
        
        # Go to next page
        if self.page_num is None:
            if self.backward: next_page_num = response.meta['page'] - 1 
            else: next_page_num = response.meta['page'] + 1
            next_page_link = self.start_url + f'-page_{next_page_num}'
            yield scrapy.Request(url=next_page_link, callback=self.parse_list_page, meta={'page': next_page_num})

    def parse_logo_page(self, response):
        item = VectorStockItem()

        item['title'] = unicodedata.normalize('NFKC', response.css('div h1::text').get()).strip()
        item['designer'] = [response.css('div.meta li.meta-artist a::text').get(),
                            urljoin(self.domain_url, response.css('div.meta li.meta-artist a::attr(href)').get())]
        item['image_id'] = response.css('div.meta li.meta-id dd::text').get()
        if self.watermark:
            item['image_urls'] = [response.meta['image_url']]
        else:
            item['image_urls'] = [response.css('div.image div.highres::attr(data-src)').get()]
        item['tags'] = response.css('div#group-keywords li a::text').getall()
        yield item
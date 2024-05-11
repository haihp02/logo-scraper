import re
import string
from urllib.parse import urljoin

import scrapy

from logo.items import LogoPondItem


class LogopondSpiderSpider(scrapy.Spider):
    name = "logopond_spider"
    allowed_domains = ["www.logopond.com", "logopond.com"]

    def __init__(self):
        super().__init__()
        self.domain_url = "https://logopond.com"
        self.info_key_map = {
            'Description:': 'description',
            'As seen on:': 'as_seen_on',
            'Status: ': 'status',
            'Viewed:': 'viewed',
            'Tags:': 'tags'
        }
    
    def start_requests(self):
        start_url = "https://logopond.com/gallery/list/?gallery=featured&filter="
        yield scrapy.Request(url=start_url, callback=self.parse_list_page)
    
    def parse_list_page(self, response):
        # Discover all logos on page
        logos = response.css('li.logo_item')
        for logo in logos:
            logo_link = logo.css('div.block > a::attr(href)').get()
            logo_link = urljoin(self.domain_url, logo_link)
            yield scrapy.Request(url=logo_link, callback=self.parse_logo_page)

        # Go to next page
        buttons = response.css('a.button')
        next_button = None
        for button in buttons:
            if button.css('::text').get() == 'next': next_button = button
        if next_button is not None:
            next_page_link = next_button.css('::attr(href)').get()
            next_page_link = urljoin(self.domain_url, next_page_link)
            yield scrapy.Request(url=next_page_link, callback=self.parse_list_page)

    def parse_logo_page(self, response):
        logo_item = LogoPondItem()

        logo_item['title'] = response.css('div#logo_info_title h2::text').get().strip()
        logo_item['designer'] = [
            response.css('div.detail_header p a::attr(title)').get(),   # nickname
            urljoin(self.domain_url, response.css('div.detail_header p a::attr(href)').get())   #url
        ]
        raw_info = response.css('div.hook p')[-1].get()
        clean_infos = clean_info_html(raw_info)
        for k in clean_infos:
            if k == "As seen on:":
                seen_on_url = response.css('div.hook p')[-1].css('a[rel=nofollow]::attr(href)').get()
                seen_on_name = clean_infos[k]
                logo_item[self.info_key_map[k]] = [seen_on_name, seen_on_url]
            else: logo_item[self.info_key_map[k]] = clean_infos[k]
        logo_item['tags'] = [text.strip() for text in response.css('div.hook p')[-1].css('a[rel!=nofollow]::text').getall()]
        logo_item['image_urls'] = [urljoin(self.domain_url, response.css('div img.swapper::attr(src)').get())]
        extra_image_urls = response.css('div img.swappes::attr(src)').getall()
        if extra_image_urls:
            logo_item['image_urls'].extend([urljoin(self.domain_url, image_url) for image_url in extra_image_urls])
        yield logo_item
        

ALL_FIELD = ["Description:", "As seen on:", "Status: ", "Viewed:", "Tags:"]
ALL_FIELD_TAGS = [f"<strong>{field}</strong>" for field in ALL_FIELD]
def clean_info_html(raw_html):
    # Get all exist field
    fields = [ALL_FIELD[i] for i in range(len(ALL_FIELD)) if ALL_FIELD_TAGS[i] in raw_html]
    field_tags = [ALL_FIELD_TAGS[i] for i in range(len(ALL_FIELD)) if ALL_FIELD_TAGS[i] in raw_html]
    fields_start_idx = [raw_html.find(field_tag) for field_tag in field_tags]

    infos = {}
    for i in range(len(fields_start_idx)):
        start_idx = fields_start_idx[i]
        if i == len(fields_start_idx) - 1:
            if fields[i] == "Tags:":
                return infos
            else:
                end_idx = len(raw_html)
        else:
            end_idx = fields_start_idx[i+1]

        content = raw_html[start_idx:end_idx]
        infos[fields[i]] = clean_text(content).replace(f'{fields[i]}', '').strip()
    return infos

control_chars = [chr(i) for i in range(32)] + [chr(127)]
def clean_text(raw_html: str):
    html_pattern = re.compile('<.*?>')
    cleantext = re.sub(html_pattern, '', raw_html)
    cleantext = cleantext.replace('\n', ' ')
    table = str.maketrans({c: '' for c in control_chars})
    cleantext = cleantext.translate(table)
    return cleantext.strip()

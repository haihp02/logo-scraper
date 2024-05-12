import os
from urllib.parse import urljoin, urlparse
from typing import Iterable
import scrapy

from scrapy_playwright.page import PageMethod
from playwright.async_api import Page as PlaywrightPage
from logo.items import DribbbleItem

username: str = os.getenv("DIBBBLE_USERNAME")
password: str = os.getenv("DIBBBLE_PASSWORD")

# For single evaluate
sign_in_script = f'''
async () => {{
    const username = document.getElementById("login")
    const password = document.getElementById("password")

    if (username && password) {{
        username.value = {username}
        password.value = {password}
    }}

    document.querySelector("input[type=submit]").click()

    // Wait until the URL changes to the expected URL after login
    await new Promise((resolve, reject) => {{
        const intervalId = setInterval(() => {{
            if (window.location.href.includes('https://dribbble.com/following')) {{
                clearInterval(intervalId);
                resolve();
            }}
        }}, 100); // Check every 100 milliseconds
    }});
}}
'''

scroll_and_show_more_script = """
async (page) => {
    while (true) {
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await new Promise(resolve => setTimeout(resolve, 2000));  // wait for lazy-loaded content to load
        const showMoreButton = await page.$('a.form-btn.load-more:has-text("Load more work")');
        if (showMoreButton) {
            await showMoreButton.click();
        } else {
            const noMoreToShow = await page.$('span.null-message');
            if (noMoreToShow) {
                return 'No more items to show';
            }
        }
    }
}
"""

class DribbbleSpiderSpider(scrapy.Spider):
    name = "dribbble_spider"
    allowed_domains = ["dribbble.com"]

    def __init__(self, start_url_file_path):
        super().__init__()
        self.domain_url = "https://www.dribbble.com"
        self.sign_in_url = "https://dribbble.com/session/new"
        with open(start_url_file_path, 'r', encoding='utf8') as f:
            self.start_urls = [line.strip() for line in f.readlines()]

    def start_requests(self):
        # Sign in
        yield scrapy.Request(
            url=self.sign_in_url,
            meta={
                'playwright': True,
                'playwright_include_page': True,
                'playwright_page_methods': [
                    PageMethod('fill', 'input[name="login"]', username),
                    PageMethod('fill', 'input[name="password"]', password),
                    PageMethod('click', 'input[type="submit"]')
                    # PageMethod('evaluate', sign_in_script)
                ],
            },
            callback=self.start_scraping,
            errback=self._errback
        )

    async def start_scraping(self, response):
        # Retrieve cookies from the page context
        # Access the Playwright page object
        page: PlaywrightPage = response.meta["playwright_page"]
        cookies = await page.context.cookies()
        # Close the page
        await page.close()
        cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}

        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                # meta={
                #     'playwright': True,
                #     'playwright_include_page': True,
                #     'playwright_page_methods': [
                #         PageMethod('evaluate', scroll_and_show_more_script)
                #     ]
                # },
                cookies=cookies_dict,
                callback=self.parse_artist_page,
                errback=self._errback
            )

    async def parse_artist_page(self, response):
        # page: PlaywrightPage = response.meta["playwright_page"]
        # # Close the page
        # await page.close()

        cookies = response.headers.getlist('Set-Cookie')
        cookies_dict = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in cookies}

        # Check if artist is pro or not
        if response.css('div.profile-masthead section.profile-promasthead'):
            pro_designer = True
            designer_name = response.css('div.masthead-profile-name h1::text').get().strip()
        elif response.css('div.profile-masthead section.profile-simple-masthead'):
            pro_designer = False
            designer_name = response.css('h1.masthead-profile-name::text').get().strip()

        all_logos = response.css('div ol li[id]')
        for logo in all_logos:
            logo_item = DribbbleItem()

            logo_item['designer'] = [designer_name, response.url]
            logo_item['title'] = logo.css('a span.accessibility-text::text').get()
            logo_item['image_urls'] = [logo.css('img[src]::attr(src)').get().split('?')[0]]
            logo_item['image_id'] = logo.attrib['data-thumbnail-id']
            logo_item['description'] = logo.css('img[src]::attr(alt)').get().strip()
            yield logo_item

            # logo_url = urljoin(self.domain_url, logo_url)
            # yield scrapy.Request(url=logo_url, callback=self.parse_logo_page, cookies=cookies_dict)
        

    def parse_logo_page(self, response):
        logo_item = DribbbleItem()

        logo_item['title'] = response.css('div h1::text').get().strip()

        image_container = response.css('section.shot-media-section div.js-media-container')
        logo_item['image_id'] = image_container.attrib['data-shot-id']
        # if multiple image, take url from gallery
        if image_container.css('div[has-gallery]'):
            images = image_container.css('li.media-gallery-thumbnail img')
            image_urls = [image.attrib['data-src'].split('?')[0] for image in images]
        else:
            image = image_container.css('div.media-content img')
            image_urls = [image.attrib['src'].split('?')[0]]
        logo_item['image_urls'] = image_urls
        yield logo_item

    async def _errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

import os
from typing import Iterable
import scrapy

from scrapy_playwright.page import PageMethod

username: str = os.getenv("DIBBBLE_USERNAME")
password: str = os.getenv("DIBBbLE_PASSWROD")

sign_in_script = f'''
const username = document.getElementById("login")
const password = document.getElementById("password)

if (username && password) {{
    username.value = 
}}

document.querySelector("input[type=submit]").click()
'''


class DribbbleSpiderSpider(scrapy.Spider):
    name = "dribbble_spider"
    allowed_domains = ["dribbble.com"]

    def __init__(self, start_url_file_path):
        super().__init__()
        self.domain_url = "https://www.dribbble.com"
        with open(start_url_file_path, 'r', encoding='utf8') as f:
            self.start_urls = [line.strip() for line in f.readlines()]

    def start_requests(self):
        # Sign in
        sign_in_url = "https://dribbble.com/session/new"


    def parse(self, response):
        pass

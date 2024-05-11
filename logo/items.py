# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field

# class LogoItem(scrapy.Item):
#     title = Field()
#     description = Field()
#     pass

class BrandsoftheworldItem(scrapy.Item):
    title = Field()
    description = Field()
    terms = Field()
    website = Field()
    designer = Field()
    contributor = Field()
    vector_format = Field()
    status = Field()
    vector_quality = Field()
    updated_on = Field()
    image_urls = Field()

class LogoPondItem(scrapy.Item):
    title = Field()
    designer = Field()
    description = Field()
    as_seen_on = Field()
    status = Field()
    viewed = Field()
    tags = Field()
    image_urls = Field()

class VectorStockItem(scrapy.Item):
    title = Field()
    designer = Field()
    image_id = Field()
    image_urls = Field()
    tags = Field()
    page = Field()

class LogobookItem(scrapy.Item):
    title = Field()
    country = Field()
    infos = Field()
    tags = Field()
    image_url = Field()
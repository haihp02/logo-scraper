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

class LogoItem(scrapy.Item):
    title = Field()
    image_urls = Field()

class BrandsoftheworldItem(LogoItem):
    description = Field()
    terms = Field()
    website = Field()
    designer = Field()
    contributor = Field()
    vector_format = Field()
    status = Field()
    vector_quality = Field()
    updated_on = Field()

class LogoPondItem(LogoItem):
    designer = Field()
    description = Field()
    as_seen_on = Field()
    status = Field()
    viewed = Field()
    tags = Field()

class VectorStockItem(LogoItem):
    designer = Field()
    image_id = Field()
    tags = Field()
    page = Field()

class LogobookItem(LogoItem):
    country = Field()
    infos = Field()
    tags = Field()

class DribbbleItem(LogoItem):
    designer = Field()
    image_id = Field()
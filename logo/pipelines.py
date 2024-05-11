# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import json

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings


class LogoPipeline:
    def process_item(self, item, spider):
        return item
    
class VectorStockPipeline:
    def __init__(self, output_filepath=None):
        self.image_ids = set()
        self.output_filepath = output_filepath
        if self.output_filepath is not None:
            self.output_filepath = os.path.join(os.curdir, self.output_filepath)
            self.image_ids = self.get_image_ids_set(self.output_filepath)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('image_id') in self.image_ids:
            raise DropItem(f'This logo has already been collected: {adapter.get("image_id")}')
        else:
            self.image_ids.add(adapter.get('image_id'))
            return item
        
    def get_image_ids_set(self, output_filepath):
        if os.path.exists(output_filepath):
            if os.path.basename(output_filepath).split('.')[-1] == 'json':
            # JSON format
                with open(output_filepath, 'r', encoding='utf8') as f:
                    meta_data = json.load(f)
                return set([item['image_id'] for item in meta_data])
            elif os.path.basename(output_filepath).split('.')[-1] == 'jsonl':
                # JSONL format
                meta_data = []
                with open(output_filepath, 'r', encoding='utf8') as f:
                    for line in f:
                        meta_data.append(json.loads(line.strip()))
                return set([item['image_id'] for item in meta_data])
        else:
            return set()
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            output_filepath=crawler.settings.get('FEED_URI', None)
        )
    
class LogobookPipeline:
    def __init__(self):
        self.image_urls = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('image_url') in self.image_urls:
            raise DropItem(f'This logo has already been collected: {adapter.get("image_url")}')
        else:
            self.image_urls.add(adapter.get('image_url'))
            return item

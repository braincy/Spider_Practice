# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.utils.project import get_project_settings
from pymongo import MongoClient


class NovelPipeline(object):
    
    def __init__(self):
        _settings=get_project_settings()
        self.client = MongoClient(_settings['MONGO_HOST'], _settings['MONGO_PORT'])
        self.db = self.client.crawler
        self.db.authenticate(_settings['MONGO_USER'], _settings['MONGO_PASSWORD'])
        pass

    def process_item(self, item, spider):
        spiderName = spider.name
        if spiderName == 'qidian':
            self._conditional_insert_novel(item)
        return item

    def _conditional_insert_novel(self, item):
        try:
            novel = self.db.novel
            novel.insert_one(item)
            print 'insert novel success'
        except Exception, e:
            print str(e)

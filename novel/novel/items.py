# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NovelItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    intro = scrapy.Field()
    score = scrapy.Field()
    title = scrapy.Field()
    cover = scrapy.Field()
    status = scrapy.Field()
    author = scrapy.Field()
    book_id = scrapy.Field()
    category = scrapy.Field()
    word_num = scrapy.Field()
    abstract = scrapy.Field()
    click_num = scrapy.Field()
    created_at = scrapy.Field()
    chapter_num = scrapy.Field()
    sub_category = scrapy.Field()
    recommend_num = scrapy.Field()
    chapter_content = scrapy.Field()
    pass

# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from scrapy.selector import Selector
from novel.items import NovelItem
from utils.oss import Oss_Adapter
from scrapy.utils.project import get_project_settings
import requests
import time
import json
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class Qidian(CrawlSpider):
    name = 'qidian'
    start_urls = [
        'https://www.qidian.com/free/all?size=1&action=1&orderId=&vip=hidden&month=3&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=1&page='+str(page) for page in range(1, {N}) 
        # N为自定义要爬取的页码范围
    ]
    
    def __init__(self):
        self.oss = Oss_Adapter()
        pass

    def parse(self, response):
        sel = Selector(response)
        element = sel.xpath('//ul[@class="all-img-list cf"]/li')
        for el in element:
            item = NovelItem()
            item['title'] = el.xpath('.//div[@class="book-mid-info"]//h4/a/text()').extract_first()
            item['author'] = el.xpath('.//p[@class="author"]//a[@class="name"]/text()').extract_first()
            item['category'] = el.xpath('.//p[@class="author"]//a[@data-eid="qd_B60"]/text()').extract_first()
            item['sub_category'] = el.xpath('.//p[@class="author"]//a[@class="go-sub-type"]/text()').extract_first()
            item['status'] = 0 if el.xpath('.//p[@class="author"]//span/text()').extract_first() == '完本' else 1
            item['url'] = 'https:' + el.xpath('.//div[@class="book-mid-info"]//h4/a/@href').extract_first()
            item['abstract'] = el.xpath('.//p[@class="intro"]/text()').extract_first().strip()
            item['word_num'] = el.xpath('.//p[@class="update"]/span/text()').extract_first()
            item['cover'] = 'https:' + el.xpath('.//div[@class="book-img-box"]/a/img/@src').extract_first()
            yield Request(url=item['url'], meta={'item':item}, callback=self.parse_details)

    def parse_details(self, response):
        item = response.meta.get('item', NovelItem())
        sel = Selector(response)
        prefix_url = 'https://book.qidian.com/ajax/comment/index?_csrfToken=noZtdawi6Zu8sYFtR2m2o3ujn4lyQLrauItBqnzG&bookId='
        item['book_id'] = item['url'][item['url'].rfind('/')+1:]
        item['score'] = json.loads(requests.get(prefix_url + item['book_id']).content)['data']['rate']
        item['intro'] = sel.xpath('//div[@class="book-info "]//p[@class="intro"]/text()').extract_first()
        click_num = sel.xpath('//div[@class="book-info "]/p[3]/em[2]/text()').extract_first()
        item['click_num'] = click_num + sel.xpath('//div[@class="book-info "]/p[3]/cite[2]/text()[1]').extract_first().replace('总点击','')
        item['chapter_num'] = int(sel.xpath('//li[@class="j_catalog_block"]//span[@id="J-catalogCount"]/text()').extract_first()[1:-2])
        recommend_num = sel.xpath('//div[@class="book-info "]/p[3]/em[3]/text()').extract_first()
        item['recommend_num'] = recommend_num + sel.xpath('//div[@class="book-info "]/p[3]/cite[3]/text()[1]').extract_first().replace('总推荐','')
        item['created_at'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item['chapter_content'] = {}
        chapter_el = sel.xpath('//div[@class="volume-wrap"]//div[@class="volume"]/ul/li')
        for i, el in enumerate(chapter_el):
            chapter_url = 'https:' + el.xpath('.//a/@href').extract_first()
            chapter_title = el.xpath('.//a/text()').extract_first()
            yield Request(url=chapter_url, meta={'item':item, 'chapter_title':chapter_title}, callback=self.parse_chapters)

    def parse_chapters(self, response):
        item = response.meta.get('item', NovelItem())
        chapter_title = response.meta.get('chapter_title').replace('.','')
        sel = Selector(response)
        content = "\n".join(sel.xpath('//div[@class="read-content j_readContent"]').xpath('string(.)').extract()).encode('utf-8').strip()
        oss_value = self.oss.uploadPage(content)
        print item['title'] + ': ' + chapter_title + '  ' + oss_value
        item['chapter_content'][chapter_title] = oss_value
        if len(item['chapter_content']) >= item['chapter_num']:
            print 'finished ' + item['title'] + ':  ' + item['author']
            yield item

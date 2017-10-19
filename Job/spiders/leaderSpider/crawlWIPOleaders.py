# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
import re
from scrapy.http import Request
from ...allitems.leaderitems import AllLeaders
import logging.config
from ...utils.Util import StrUtil
logger = logging.getLogger('ahu')

class WIPOleadersSpider(scrapy.Spider):
    name = "WIPOleaders"

    start_urls = ["http://www.wipo.int/about-wipo/en/management.html"]
    def __init__(self):
        logger.debug("开始爬取WIPO领导人信息")

    def parse(self, response):
        selector = scrapy.Selector(response)
        datas = selector.xpath('//div[@class="content line"]')
        if datas:
            for data in datas[:-1]:
                item = self._inititem()
                item["url"] = response.url
                ns = data.xpath('h2/text()').extract()
                pdf_url = data.xpath('//p/a')
                urls = pdf_url.xpath("@href").extract()
                for url in urls:
                    if re.match(r'.*pdf#page.*',url):
                        pdf_url = url
                        break
                if ns:
                    if '-' in ns[0]:
                        item["name"] = StrUtil.delWhiteSpace(ns[0].split('-')[0])
                        item["department"] = StrUtil.delWhiteSpace(ns[0].split('-')[1])
                    else:
                        item["name"] = StrUtil.delWhiteSpace(ns[0].split('–')[0])
                        item["department"] = StrUtil.delWhiteSpace(ns[0].split('–')[1])

                work = data.xpath('ul').xpath('string(.)').extract()
                if work:
                    item["work"] = StrUtil.delWhiteSpace(work[0])
                yield Request(url=pdf_url, callback=self.savepdf, meta={'item': item}, dont_filter=True)
                logger.debug('>>>WIPOleader>>>name>>>%s' % item["name"])
                logger.debug('>>>WIPOleader>>>department>>>%s' % item["department"])
                logger.debug('>>>WIPOleader>>>work>>>%s' % item["work"])
                yield item
        else:
            logger.error('爬取WIPO领导人姓名和部门失败')

    def savepdf(self, response):
        item = response.meta['item']
        with open('./WIPOPDF/' + item['name'] + '.pdf', 'wb') as f:
            f.write(response.body)

    def _inititem(self):
        '''
        初始化全部字段
        :return: 初始字段
        '''
        item = AllLeaders()
        item["work"] = ""
        item["name"] = ""
        item["department"] = ""
        item["englishname"] = "WIPO"
        item["url"] = ""
        item["resume"] = ""
        logger.info('初始化WIPO领导人item成功')
        return item
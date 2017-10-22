# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
import logging.config
from ..baseSpider import baseSpider
from scrapy.http import Request
from ...utils.Util import StrUtil
logger = logging.getLogger('ahu')

class CERNjobsSpider(baseSpider):
    name = 'CERNjob'
    start_urls = [
        'http://jobs.web.cern.ch/latest-jobs?page=0',
        'http://jobs.web.cern.ch/latest-jobs?page=1']
    
    def __init__(self,*a, **kw):
        super(CERNjobsSpider, self).__init__(*a, **kw)
        logger.debug('开始爬取CERN岗位信息')

    def parse(self, response):
        selector = scrapy.Selector(response)
        links = selector.xpath("//table[@class='views-view-grid cols-1']/tbody/tr/td/div[1]/span/a/@href").extract()
        for link in links:
            logger.debug('开始爬取%s' % link)
            yield Request(url=link, callback=self.parseDetials)

    def parseDetials(self, response):
        '''
        页面提取器，解析字段
        '''
        item = self.initItem()
        selector = scrapy.Selector(response)
        item['joburl'] = response.url
        item['incontinent'] = '欧洲'
        item['alljoburl'] = 'http://jobs.web.cern.ch/content/join-us'
        item['type'] = '物理'
        item['englishname'] = 'CERN'
        item['chinesename'] = '欧洲核子国际组织'
        item['url'] = 'https://home.cern/'
        item['incountry'] = '瑞士'
        con = selector.xpath("//div[@class='views-row views-row-1 views-row-odd views-row-first views-row-last']")
        item['work'] = ' '.join(con[0].xpath("div[@class='views-field views-field-title']/span/h1/text()").extract())
        item['issuedate'] = ' '.join(con[0].xpath("div[@class='views-field views-field-field-job-pub-date']/div/span/text()").extract())
        item['ApplicationDeadline'] = ' '.join(con[0].xpath("div[@class='views-field views-field-field-job-date-closed']/div/span/text()").extract())
        item['description'] = ' '.join(con[0].xpath("div[@class='views-field views-field-field-job-intro-en']/div//p").xpath('string(.)').extract()) + ' '.join(con[0].xpath("div[@class='views-field views-field-field-job-intro-en']/div//ul/li/text()").extract())
        if item['description']:
            item['responsibilities'] = ' '.join(con[0].xpath("div[@class='views-field views-field-field-job-function-en']/div/ul//li/text()").extract())
            item['education'] = ' '.join(con[0].xpath("div[@class='views-field views-field-field-job-qualification-en']/div//p/text()").extract())
            experience_ability = con[0].xpath("div[@class='views-field views-field-field-job-experience-en']/div[@class='field-content']").xpath('string(.)').extract()
            content = str(experience_ability)
            content = ' '.join(content.split('\n'))
            info1 = content.split('The experience required for this post is:')

            if info1[0] == '[]':
                info1 = content
            info2 = info1[-1].split('The technical competencies required for this post are:')
            if info2[0] != '[]':
                item['experience'] = info2[0]
            else:
                info2 = info1
            info3 = info2[-1].split('The behavioural competencies required for this post are:')
            if info3[0] != '[]':
                item['skill'] = info3[0]
            else:
                info3 = info2
            info4 = info3[-1].split('The language competencies required are:')

            if info4[0] != '[]':
                item['language'] = info4[-1]
            item['addition'] = ' '.join(con[0].xpath("div[@class='views-field views-field-field-job-eligibility-en']/div//p/text()").extract())
            item = {k: StrUtil.delWhiteSpace(item[k]) for k in item.keys()}
            self.debugItem(item)
            self.insert(item,spiderName=self.name)
        else:
            item['description'] = ' '.join(con[0].xpath("div[@class='views-field views-field-field-job-descr']/div[@class='field-content']/p/text()").extract())
            item['education'] = ' '.join(con[0].xpath("div[@class='views-field views-field-field-job-eligibility-en']/div[@class='field-content']").xpath('string(.)').extract())
            item['TypeofContract'] = ' '.join(con[0].xpath("div[@class='views-field views-field-field-job-progr-important-info-e']/div[@class='field-content']").xpath('string(.)').extract())
            item['addition'] = ' '.join(con[0].xpath("div[@class='views-field views-field-field-job-progr-selection-en']/div[@class='field-content']").xpath('string(.)').extract())
            item = {k: StrUtil.delWhiteSpace(item[k]) for k in item.keys()}
            self.debugItem(item)
            self.insert(item, spiderName=self.name)

# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
try:
    from bs4 import BeautifulSoup
except:
    import BeautifulSoup
from selenium import webdriver
from ..baseSpider import baseSpider
import time
import logging.config
logger = logging.getLogger('ahu')
class ITERJobSpider(baseSpider):

    name = 'ITERjob'
    start_urls = ["http://www.iter.org/jobs"]
    def __init__(self,*a, **kw):
        super(ITERJobSpider, self).__init__(*a, **kw)
        logger.debug("准备爬取ITER(国际热核聚变实验堆计划)岗位数据")
        self.driver = webdriver.PhantomJS()
        # self.driver = webdriver.Chrome()
        self.driver.maximize_window()

        # 字段对应表
        self.matchingDict = {'work':'Jobtitle',
                             'belong':'Department',
                             'ApplicationDeadline':'Application Deadline (MM/DD/YYYY)',
                             'PostLevel':'Grade',
                             'responsibilities':'Main duties / Responsibilities',
                             'description':'Purpose',
                             'education':['Level of study','Diploma'],
                             'experience':['Level of experience','Technical experience/knowledge'],
                             'skill':['Social skills','Specific skills','General skills'],
                             'addition':'Others',
                             'language':'Languages'}

    def parse(self,response):
        '''
        页面提取器，抽取全部待爬岗位的链接
        '''
        selector = scrapy.Selector(response)
        for tr in selector.xpath('//table[@class="table"]/tr')[1:]:
            '''遍历每个岗位'''
            link = tr.xpath('td[1]/a/@href').extract()[0]
            logger.debug("准备爬取%s"%link)
            self.driver.get(link)
            time.sleep(2)
            item = self.initItem()
            item['joburl'] = link
            item['incontinent'] = '欧洲'
            item['alljoburl'] = 'http://www.iter.org/jobs'
            item['type'] = '能源'
            item['englishname'] = 'ITER'
            item['chinesename'] = '国际热核聚变实验堆计划'
            item['url'] = 'http://www.iter.org/proj/inafewlines#5'
            item['incountry'] = '法国'
            itemDict = self.crawlJobDetailPage(self.driver.page_source)

            # todo 整理字段,倒入新定义的item
            for each in self.matchingDict.keys():
                if isinstance(self.matchingDict[each],str):
                    if itemDict.has_key(self.matchingDict.get(each)):
                        item[each] = itemDict[self.matchingDict.get(each)]
                elif isinstance(self.matchingDict[each],list):
                    for _ in self.matchingDict.get(each):
                        if itemDict.has_key(_):
                            item[each] += itemDict[_]
            # self.debugItem(item)
            self.insert(item, spiderName=self.name)

    def crawlJobDetailPage(self,res):
        '''
        页面提取器，解析字段
        '''
        soup = BeautifulSoup(res, 'html.parser')
        tr = soup.find('div', id='subform').find('table').find('tbody').find_all('tr')
        item = {}
        item['Division'] = ""
        item['Diploma'] = ""
        item['Others'] = ""
        item['Jobtitle'] = tr[0].find('td').find('h3').find('span').text
        trs = tr[1].find('td').find('table').find('tbody').find_all('tr')
        for t in trs:
            try:
                td = t.find_all('td')
                key = td[0].find('div').find('span').text
                value = td[1].find('span').text
                item[key] = value
            except:
                pass
        return item

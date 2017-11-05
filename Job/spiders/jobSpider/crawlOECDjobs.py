# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
from selenium import webdriver
from scrapy.http import HtmlResponse
from ..baseSpider import baseSpider
from ...utils.Util import StrUtil
import re
import time
import logging.config
logger = logging.getLogger('ahu')

class OECDJobSpider(baseSpider):
    name = 'OECDjob'
    start_urls = []

    def __init__(self,*a, **kw):
        super(OECDJobSpider, self).__init__(*a, **kw)
        logger.debug("开始爬取OECD(经济合作与发展组织)岗位数据")
        # self.driver = webdriver.PhantomJS()
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.isHeader = {}

    def start_requests(self):
        self.driver.get("https://oecd.taleo.net/careersection/ext/joblist.ftl")
        res = HtmlResponse(url='my HTML string', body=self.driver.page_source, encoding="utf-8")
        trs = res.xpath('//div[@id="requisitionListInterface.listRequisitionContainer"]/table//tr[@class="ftlcopy ftlrow"]')
        logger.debug("OECD共有%s条岗位数据待爬"%len(trs))
        simpleInfo = {}
        for i in range(0,len(trs)-1,1):
            work = trs[i].xpath('td[2]/div/div[1]/div[1]/div/h2/span/a/text()').extract()[0]
            self.isHeader[work] = False
            belong = trs[i].xpath('td[2]/div/div[1]/div[2]/span[1]/text()').extract()[0]
            Location = trs[i].xpath('td[2]/div/div[1]/div[2]/div/span/text()').extract()[0]
            issuedate = trs[i].xpath('td[2]/div/div[1]/div[3]/span[3]/text()').extract()[0]
            ApplicationDeadline = trs[i].xpath('td[2]/div/div[1]/div[4]/span[3]/text()').extract()[0]
            simpleInfo[work] = {
                'belong':belong,
                'Location':Location,
                'issuedate':issuedate,
                'ApplicationDeadline':ApplicationDeadline
            }
        frist_job_text = res.xpath('//a[@id="requisitionListInterface.reqTitleLinkAction.row1"]/text()').extract()[0]
        self.driver.find_element_by_link_text(frist_job_text).click()
        time.sleep(2)
        if frist_job_text in self.driver.page_source:
            self.isHeader[frist_job_text] = True
            self.details(
                self.driver.page_source,
                frist_job_text,
                simpleInfo[frist_job_text]['belong'],
                simpleInfo[frist_job_text]['Location'],
                simpleInfo[frist_job_text]['issuedate'],
                simpleInfo[frist_job_text]['ApplicationDeadline'])

        while True:
            self.driver.find_element_by_link_text("Next").click()
            res = HtmlResponse(url='my HTML string', body=self.driver.page_source, encoding="utf-8")
            work = res.xpath('//span[@id="requisitionDescriptionInterface.reqTitleLinkAction.row1"]/text()').extract()[0]
            if not self.isHeader[work]:
                self.details(
                    self.driver.page_source,
                    work,
                    simpleInfo[work]['belong'],
                    simpleInfo[work]['Location'],
                    simpleInfo[work]['issuedate'],
                    simpleInfo[work]['ApplicationDeadline'])
                self.isHeader[work] = True
            if not False in self.isHeader.values():
                self.depose()
                logger.debug('OECD爬取结束')
                break

    def depose(self):
        '''
       关闭浏览器  
        '''
        self.driver.close()

    def details(self,page_source,work,belong,Location,issuedate,ApplicationDeadline):
        '''
        页面提取器，解析字段
        '''
        item = self.initItem()
        item["englishname"] = "OECD"
        item["chinesename"] = "经济合作与发展组织"
        item["incontinent"] = "欧洲"
        item["incountry"] = "法国"
        item["type"] = "经济"
        item["url"] = "http://www.oecd.org/"
        item["alljoburl"] = "https://oecd.taleo.net/careersection/ext/joblist.ftl"
        item['joburl'] = "https://oecd.taleo.net/careersection/ext/joblist.ftl"
        item["work"] = work
        item['belong'] = belong
        item['Location'] = Location
        item['issuedate'] = issuedate
        item['ApplicationDeadline'] = ApplicationDeadline
        res = HtmlResponse(url='my HTML string', body=page_source, encoding="utf-8")
        selector = scrapy.Selector(res)
        def getInfo(*args):
            try:
                item[args[0]] = args[1].group(1)
                if args[0] == 'education':
                    item[args[0]] = args[1].group(2)
            except:
                pass
        data = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(selector.xpath('//div[@id="requisitionDescriptionInterface.ID1408.row1"]').xpath('string(.)').extract()[0]))
        getInfo('description',re.match(r'(.*)([Mm]ain [Rr]esponsibilities)|(Date and time)',data))
        getInfo('responsibilities',re.search(r'[Mm]ain\s+[Rr]esponsibilities(.*)[Ideal](.|\s){,50}\s+[Pp]rofile',data))
        getInfo('education',re.search(r'[Ideal](.|\s){,50}\s+[Pp]rofile(.*?)[Ll]anguages',data))
        getInfo('language',re.search(r'[Ll]anguages(.*?)[Cc]ore [Cc]ompetencies',data))
        getInfo('skill',re.search(r'[Cc]ore [Cc]ompetencies(.*?)[Cc]ontract [Dd]uration',data))
        getInfo('contracttime',re.search(r'[Cc]ontract [Dd]uration(.*?)[Ww]hat [Tt]he OECD [Oo]ffers',data))
        self.debugItem(item)
        self.insert(item,spiderName=self.name)

    
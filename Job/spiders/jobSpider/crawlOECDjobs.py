# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
from selenium import webdriver
from scrapy.http import HtmlResponse
from ..baseSpider import baseSpider
from ...utils.Util import StrUtil
import time
import re
import logging.config
logger = logging.getLogger('ahu')

class OECDJobSpider(baseSpider):
    name = 'OECDjob'
    start_urls = ["https://oecd.taleo.net/careersection/ext/joblist.ftl"]

    def __init__(self,*a, **kw):
        super(OECDJobSpider, self).__init__(*a, **kw)
        logger.debug("开始爬取OECD(经济合作与发展组织)岗位数据")
        # self.driver = webdriver.PhantomJS()
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

    def parse(self, response):
        self.driver.get(response.url)
        main_page = self.driver
        time.sleep(5)
        main_page.implicitly_wait(30)
        res = HtmlResponse(url='my HTML string', body=main_page.page_source, encoding="utf-8")
        trs = res.xpath('//table[@id="requisitionListInterface.listRequisition"]/tbody/tr')
        page_len = len(trs)/2
        click_text = res.xpath('//a[@id="requisitionListInterface.reqTitleLinkAction.row1"]/text()').extract()[0]
        main_page.find_element_by_partial_link_text(click_text).click()
        time.sleep(3)
        self.details(main_page.page_source)
        for i in range(0,page_len - 1):
            main_page.find_element_by_partial_link_text("Next").click()
            time.sleep(2)
            self.details(main_page.page_source)

    def details(self,page_source):
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

        res = HtmlResponse(url='my HTML string', body=page_source, encoding="utf-8")
        selector = scrapy.Selector(res)
        # 岗位名称
        workdata = selector.xpath('//div[@class="editablesection"]/div[1]')
        workinfo = workdata.xpath('string(.)').extract()
        item["work"] = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(workinfo[0]))


        # 其他岗位信息
        otherdata = selector.xpath('//span[@id="requisitionDescriptionInterface.ID1451.row1"]')
        require =   re.sub('\n',' ',otherdata.xpath('string(.)').extract()[0])

        info1 = require.split('Main Responsibilities')
        for i in info1[:-1]:
            item['description'] += i
        item['description'] = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(item['description']))

        info2 = info1[-1].split('Ideal Candidate profile')
        for i in info2[:-1]:
            item['responsibilities'] += i
        item['responsibilities'] = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(item['responsibilities']))

        info3 = info2[-1].split('Contract Duration')
        for i in info3[:-1]:

            item["IdealCandidateProfile"] += i
        item["contracttime"] = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(item["IdealCandidateProfile"]))

        if 'What the OECD offers' in info3[-1]:
            info4 = info3[-1].split('What the OECD offers')
            item["contracttime"] = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(info4[0]))
            item["treatment"] = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(info4[1]))
        else:
            item["contracttime"] = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(info3[-1]))
        print item
        self.debugItem(item)
        self.insert(item,spiderName=self.name)

    def depose(self):
        '''
       关闭浏览器  
        '''
        self.driver.close()
    
# -*- coding: utf-8 -*-

import logging.config
import re
import sys
from ...utils.Util import StrUtil
from ..baseSpider import baseSpider
import scrapy
from scrapy_splash import SplashRequest
logger = logging.getLogger('ahu')

class WIPOjobSpider(baseSpider):

    name = "WIPOjob"
    start_urls = []

    def __init__(self,*a, **kw):
        super(WIPOjobSpider, self).__init__(*a, **kw)
        logger.debug("准备爬取:WIPO(世界知识产权组织)招聘岗位信息")

    def start_requests(self):
        yield SplashRequest(url="https://wipo.taleo.net/careersection/wp_2/jobsearch.ftl?lang=en#",
                            callback=self.parselink,
                            args={'wait': 2})

    def parselink(self, response):
        '''
        页面提取器，
        提取招聘岗位链接，迭代爬取
        '''
        job = scrapy.Selector(response)
        links = job.xpath('//div[@class="multiline-data-container"]/div/span/a/@href').extract()
        logger.info("WIPO共" + str(len(links)) + "条网页待爬")
        for link in links:
            logger.debug("WIPO待爬岗位:  " + "https://wipo.taleo.net" + link)
            url = 'https://wipo.taleo.net' + link

            '''splash渲染，该网站响应较慢，如渲染失败，可适当增长延迟时间
              wait->3
            '''
            yield SplashRequest(url=url,
                                callback=self.parsejob,
                                args={'wait': 5})

    def parsejob(self,response):
        '''
        页面提取器，解析字段
        '''
        item = self.initItem()
        item["englishname"] = "WIPO"
        item["chinesename"] = "世界知识产权组织"
        item["incontinent"] = "欧洲"
        item["incountry"] = "瑞士"
        item["type"] = "知识产权"
        item["url"] = "http://www.wipo.int/portal/en/index.html"
        item["alljoburl"] = "https://wipo.taleo.net/careersection/wp_2/jobsearch.ftl?lang=en#"
        item["joburl"] = response.url
        response = scrapy.Selector(response)

        work = response.xpath('//div[@class="editablesection"]/div[1]').xpath('string(.)').extract()[0]
        item["work"] = re.sub('\W', '', work.split('-')[0])  # 岗位

        sector = response.xpath('//div[@class="editablesection"]/div[2]').xpath('string(.)').extract()[0]
        item["belong"] = sector  # 部门、组织机构

        grade = response.xpath('//div[@class="editablesection"]/div[3]').xpath('string(.)').extract()[0]
        item["PostLevel"] = re.sub('\W', '', grade.split('-')[1])  # 职级

        contract = response.xpath('//div[@class="editablesection"]/div[4]').xpath('string(.)').extract()[0]
        item["contracttime"] = re.sub('\W', '', contract.split('-')[-1])  # 合同期限

        DutyStation = response.xpath('//div[@class="editablesection"]/div[5]').xpath('string(.)').extract()[0]
        item["Location"] = re.sub('\W', '', DutyStation.split(':')[-1])  # 工作地点

        time = response.xpath('//div[@class="editablesection"]/div[6]').xpath('string(.)').extract()[0]  # 时间
        item["issuedate"] = re.sub('\W', '', time.split('Application Deadline')[0].split(':')[-1])  # 发布时间
        item["ApplicationDeadline"] = re.sub('\W', '', time.split('Application Deadline')[-1])  # 截止时间

        requireinfo = response.xpath('//div[@class="editablesection"]/div[7]')
        require = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(re.sub('\n', ' ', requireinfo.xpath('string(.)').extract()[0])))

        item["description"] = re.search(r"Organizational(.*)Duties and responsibilities",require,re.I).group(0).strip('Duties and responsibilities')  # 组织背景

        item["responsibilities"] = re.search(r"Duties and responsibilities(.*)Requirements",require,re.I).group(0).strip('Requirements')  # 职能

        Requirements = re.search(r"Requirements(.*)Organizational competencies",require,re.I).group(0)  # 要求

        item["experience"] = re.search(r'Experience(.*)Languages',Requirements,re.I).group(0).strip('Languages')

        item["education"] =  re.search(r'Education(.*)Experience Ess',Requirements,re.I).group(0).strip('Experience Ess') #教育背景

        item["language"] = re.search(r'Languages(.*)Job-related',Requirements,re.I).group(0).strip('Job-related')  #语言

        item["skill"] = re.search(r"Job-related(.*)Information",require,re.I).group(0).strip('5. Information')    #技能

        item["addition"] = StrUtil.delMoreSpace(
            StrUtil.delWhiteSpace(require.split('Organizational context')[-1].split
                                  ('Duties and responsibilities')[-1].split('Requirements')[-1].split(
                'Organizational competencies')[-1].split('Information')[-1]))  #附加信息
        self.debugItem(item)
        self.insert(item,spiderName=self.name)
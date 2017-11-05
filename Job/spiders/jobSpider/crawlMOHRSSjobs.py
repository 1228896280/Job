# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
try:
    from bs4 import BeautifulSoup
except:
    import BeautifulSoup
import re
from ..baseSpider import baseSpider
from ...utils.Util import StrUtil
from scrapy import Request
import logging.config
logger = logging.getLogger('ahu')
class MOHRSSJobSpider(baseSpider):

    name = 'MOHRSSjob'
    start_urls = []

    def __init__(self, *a, **kw):
        super(MOHRSSJobSpider, self).__init__(*a, **kw)
        self.preurl = "http://www.mohrss.gov.cn/SYrlzyhshbzb/rdzt/gjzzrcfw/gwkqxx"
        self.start_urls.append('http://www.mohrss.gov.cn/SYrlzyhshbzb/rdzt/gjzzrcfw/gwkqxx/index.html')
        for i in range(1,25,1):
            self.start_urls.append('http://www.mohrss.gov.cn/SYrlzyhshbzb/rdzt/gjzzrcfw/gwkqxx/index_%s.html'%i)

    def parse(self, response):
        '''
        遍历首页的全部岗位，准备迭代爬取，参考
        http://www.mohrss.gov.cn/SYrlzyhshbzb/rdzt/gjzzrcfw/gwkqxx/index.html
        '''
        selector = scrapy.Selector(response)
        pageLinks = selector.xpath('//div[@class="main_left_m"]/ul/li')
        for eachLink in pageLinks:
            url = self.preurl + eachLink.xpath('a/@href').extract()[0].strip('.')
            # logger.debug("待爬链接：" + url)
            yield Request(url=url,callback=self.parseMoreInfo,dont_filter=True)

    def parseMoreInfo(self,response):
        '''
        页面提取器，提取详情页，参考
        http://www.mohrss.gov.cn/SYrlzyhshbzb/rdzt/gjzzrcfw/gwkqxx/201710/t20171017_279342.html
        '''
        selector = scrapy.Selector(response)
        moreInfoPage = re.search(r'https:\/\/careers\.un\.org\/lbw\/jobdetail\.aspx\?id=\d{5}',response.body,re.I).group(0)
        org = selector.xpath('//div[@class="main_er"]/h2/text()').extract()[0]
        yield Request(url=moreInfoPage,callback=self.parseJob,meta={"org":org})

    def parseJob(self,res):
        '''
        页面提取器，解析字段
        '''
        selector = scrapy.Selector(res)
        item = self.initItem()
        item['joburl'] = res.url
        item['incontinent'] = '北美洲'
        item['alljoburl'] = 'http://www.mohrss.gov.cn/SYrlzyhshbzb/rdzt/gjzzrcfw/gwkqxx/'
        item['type'] = '国际关系'
        item['englishname'] = 'UN'
        item['url'] = 'http://www.mohrss.gov.cn/SYrlzyhshbzb/rdzt/gjzzrcfw/'
        item['incountry'] = '美国'
        item['chinesename'] = res.meta["org"].split('空缺')[0]
        item["PostLevel"] = re.search(r'[P,D,G].*\d', res.meta["org"], re.I).group(0)  # 职级
        trs = selector.xpath('//table[@id="JobDescription"]/tr')
        title = trs[0].xpath('td[2]/span/text()').extract()[0]
        item["work"] = title  # 岗位
        item["belong"] = trs[2].xpath('td[2]/span/text()').extract()[0] #部门
        item["Location"] = trs[3].xpath('td[2]/span/text()').extract()[0]  # 工作位置
        time = trs[4].xpath('td[2]/span/text()').extract()[0]  # 工作位置
        item["issuedate"] = time.split('-')[0]  # 发布时间
        item["ApplicationDeadline"] = time.split('-')[1] #截止时间
        text = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(selector.xpath('//div[@id="jd_content"]').xpath('string(.)').extract()[0]))
        item["responsibilities"] = re.search(r'Responsibilities(.*)Competencies', text).group(0).strip('Competencies')  # 职责
        item["description"] = re.search(r'Special\s+Notice(.*)Org\.\s+Setting\s+and\s+Reporting', text).group(0).strip('Org.Setting and Reporting')  # 描述
        item["skill"] = re.search(r'Competencies(.*)Education', text).group(0).strip('Education')  # 技能
        item["education"] = 'E' + re.search(r'Education(.*)Work\s+Experience', text).group(0).strip('Work Experience')  # 教育背景
        item["experience"] = re.search(r'Work\s+Experience(.*)Languages', text).group(0).strip('Languages')  # 工作经历
        item["language"] = re.search(r'Languages(.*)Assessment', text).group(0).strip('Assessment')  # 语言
        item["addition"] = re.search(r'United\s+Nations\s+Considerations(.*?)No\s+Fee', text).group(0).strip('No Fee')  # 附加信息
        # self.debugItem(item)
        self.insert(item,self.name)
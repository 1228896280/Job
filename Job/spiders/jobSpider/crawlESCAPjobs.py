# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
import logging.config
from ..baseSpider import baseSpider
import re
from scrapy_splash import SplashRequest
from ...utils.Util import StrUtil
logger = logging.getLogger('ahu')

class ESCAPjobsSpider(baseSpider):
    name = 'ESCAPjob'
    start_urls = ["http://www.unescap.org/jobs"]

    def __init__(self,*a, **kw):
        super(ESCAPjobsSpider, self).__init__(*a, **kw)
        logger.debug('开始爬取ESCAP岗位信息')
        self.headers = {
            'Cookie':'__utma=114554307.1115320938.1506329283.1508563782.1508563782.1; __utmz=114554307.1508563782.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); citrix_ns_id_.un.org_%2F_wlf=AAAAAAU-8naEc_HrcageIHBBAHzCMW0qBGmhomHkpHOrZr_OtnjtNEEpD4BusZQZZHcKTjUDMi2oe8iGJuqHXhjzQmww6lwyakvt-0_pg1omYvteRg==&AAAAAAWHBNAKXsxcHMe_uI3AhLJs2GNkIAiITf1UWkyMYAWnVjKEtQoVwnvdyUbQUIsY3NIvGSL3do3hpmjeR4J3T2VUTd2l1Jz6ehVoKV8xYyRSO3r5uCjRoSgrh30OWpZJJTc=&; vmpodunat026-30011-PORTAL-PSJSESSIONID=SJBDzzTJoVOsnnZtlx1Ond5Y6kBBigX_!2078676610; ExpirePage=https://inspira.un.org/psc/UNCAREERS/; PS_LOGINLIST=https://inspira.un.org/UNCAREERS; PS_TOKEN=qwAAAAQDAgEBAAAAvAIAAAAAAAAsAAAABABTaGRyAk4AdQg4AC4AMQAwABQHL60tDU6FSDnuM1d9nr/3JATiTWsAAAAFAFNkYXRhX3icHYo5CoBAEATLVQyN/Iaiux4YGngEIuIBZr7C3/k4m52B6mJ6XiAKTRAoP4Of9GJl4OYUd3nPQjxIJpKNg1HNw6yushSUtGRiIVptJnPkunSi817rp/GthR/7gAy8; SignOnDefault=; BIGipServer~Public~inspira_un_org_http=rd1o00000000000000000000ffff89fea869o10069; _ga=GA1.2.1115320938.1506329283; _gid=GA1.2.1651592158.1508671384; psback=""url":"https%3A%2F%2Finspira.un.org%2Fpsc%2FUNCAREERS%2FEMPLOYEE%2FHRMS%2Fc%2FUN_CUSTOMIZATIONS.UN_JOB_DETAIL.GBL" "label":"zzz" "origin":"PIA""; PS_TOKENEXPIRE=22_Oct_2017_12:29:11_GMT; BIGipServerinspiracareer_un_oracle_com_30010_30011=133306256.15221.0000',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
        }

    def parse(self, response):
        selector = scrapy.Selector(response)
        links = selector.xpath('//div[@class="attachment attachment-before"]//a')
        for _ in links:
            link = _.xpath('@href').extract()[0]
            # logger.debug('准备爬取链接%s'%link)
            yield SplashRequest(url=link,
                                callback=self.parseBody,
                                headers=self.headers,
                                args={
                                    'wait': 3
                                })

    def parseBody(self,response):
        _ = {
            'Posting Title:':'work',
            'Department/ Office:':'belong',
            'Duty Station:':'Location',
            'Posting Period:':'time',
        }
        selector = scrapy.Selector(response)
        item = self.initItem()
        item['incontinent'] = '亚洲'
        item['joburl'] = response.url
        item['alljoburl'] = 'http://www.unescap.org/jobs'
        item['type'] = '经济'
        item['englishname'] = 'ESCAP'
        item['chinesename'] = '亚太经社会'
        item['url'] = 'http://www.unescap.org/'
        item['incountry'] = '泰国'
        trs = selector.xpath('//div[@id="win0div$ICField3$0"]/table[@class="PABACKGROUNDINVISIBLE"]/tbody/tr')[1:]
        for i in range(0,len(trs),2):
            try:
                k = trs[i].xpath('td[2]/div/span/text()').extract()[0]
                if k in _.keys():
                    item[_[k]] = trs[i+1].xpath('td[2]/div/span/text()').extract()[0]
                else:
                    continue
            except:
                k = trs[i].xpath('td[2]/div/label/text()').extract()[0]
                if k in _.keys():
                    item[_[k]] = trs[i+1].xpath('td[2]/div/span/text()').extract()[0]
                else:
                    continue
        item['PostLevel'] = re.search(r'[DPG][0-9]',item['work']).group(0)
        item['issuedate'] = item['time'].split('-')[0]
        item['ApplicationDeadline'] = item['time'].split('-')[1]

        texts = selector.xpath('//div[@id="win0divHRS_JO_PST_DSCR$0"]/table[@class="PABACKGROUNDINVISIBLE"]/tbody/tr')[2:]
        __ = {
            'Responsibilities':'responsibilities',
            'responsibilities':'skill',
            'Education':'education',
            'Work Experience':'experience',
            'Languages':'language',
            'United Nations Considerations':'addition',
            'Org. Setting and Reporting':'description'
        }
        for i in range(0, len(texts), 4):
            k = texts[i].xpath('td[2]/div/span/text()').extract()[0]
            if k in __.keys():
                item[__[k]] = ' '.join(StrUtil.delWhiteSpace(texts[i+2].xpath('string(.)').extract()[0]).split())
            else:
                continue
        self.debugItem(item)
        self.insert(item,spiderName=self.name)


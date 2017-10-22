# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
import re
from scrapy.http import Request
from scrapy_splash import SplashRequest
import logging.config
from ..baseSpider import baseSpider
from ...utils.Util import StrUtil
logger = logging.getLogger('ahu')
class UNDPjobSpider(baseSpider):
    name = "UNDPjob"
    start_urls = ["https://jobs.undp.org/cj_view_jobs.cfm"]

    def __init__(self,*a, **kw):
        super(UNDPjobSpider, self).__init__(*a, **kw)
        self.preurl = "https://jobs.undp.org/"

    def parse(self, response):
        selector = scrapy.Selector(response)
        logger.debug("开始解析UNDP(联合国开发计划蜀)的连接信息")
        table = selector.xpath('//div[@id="content-main"]/table[@class="table-sortable"]')
        for evertable in table:
            tbody = evertable.xpath('tr')
            for everlink in tbody[:-1]:
                # 提取具体岗位连接
                link = everlink.xpath('td[1]/a/@href').extract()
                if len(link):
                    if link[0].startswith('c'):
                        LINK = self.preurl + link[0]
                    else:
                        LINK = link[0]
                else:
                    continue
                # 提取岗位描述信息
                describe = everlink.xpath('td[1]/a/text()').extract()
                DESERIBE = describe[0] if len(describe) else ""
                # 提取所属系统(第二列)
                suoshu = everlink.xpath('td[2]/text()').extract()
                SUOSHU = suoshu[0] if len(suoshu) else ""
                # 提取岗位名称
                work = everlink.xpath('td[3]/text()').extract()
                WORK = work[0].strip() if len(work) else ""
                # 提取岗位申请时间
                applytime = everlink.xpath('td[4]/text()').extract()
                APPLYTIME = applytime[1] if len(applytime) else ""
                if LINK.endswith('id=2'):

                    logger.debug("开始爬取链接%s"%LINK)
                    # todo 使用splash进行js页面渲染
                    yield SplashRequest(url=LINK,
                                    callback=self._crawliframe,
                                    meta={"describe":DESERIBE,
                                            "suoshu":SUOSHU,
                                            "applytime":APPLYTIME,},
                                  args={'wait': 2})

                else:
                    logger.debug("开始爬取链接%s" % LINK)
                    yield Request(url=LINK,
                                    callback=self._UNDPprase,
                                    meta={"describe":DESERIBE,
                                                "suoshu":SUOSHU,
                                                "work":WORK,
                                                "applytime":APPLYTIME,}
                                          )

    def _UNDPprase(self, response):
        '''
        抽取不带*岗位页面
        '''
        logger.debug('crawl noid!')
        job = scrapy.Selector(response)
        item = self.initItem()
        item["joburl"] = response.url
        item["PostLevel"] = response.meta["work"]
        item["work"] = response.meta["describe"]
        item["belong"] = response.meta["suoshu"]
        item["issuedate"] = response.meta["applytime"]
        item['incontinent'] = '北美洲'
        item['alljoburl'] = 'https://jobs.undp.org/cj_view_jobs.cfm'
        item['type'] = '科学研究'
        item['englishname'] = 'UNDP'
        item['chinesename'] = '联合国开发计划署'
        item['url'] = 'http://www.undp.org/'
        item['incountry'] = '美国'
        self._crawlnoid(job,item)
        self.debugItem(item)
        self.insert(item,spiderName=self.name)

    def _crawlnoid(self,job,item):
        '''
        页面提取器，解析字段，针对非*岗位
        '''
        noidziduan = {'Location :':'Location',
                      'Application Deadline :':'ApplicationDeadline',
                      'Type of Contract :':'TypeofContract',
                      'Languages Required :':'language',
                      'Duration of Initial Contract :':'contracttime',
                      'Expected Duration of Assignment :':'ExpectedDurationofAssignment'}

        textnfo_noid = {'Background':'description',
                        'Duties and Responsibilities':'responsibilities',
                        'Competencies':'skill',}

        #TODO  提取基本信息
        trs = job.xpath('//div[@id="content-main"]/table[1]/tr')
        for tr in trs:
            ziduanming = tr.xpath('td[1]/strong/text()').extract()
            if ziduanming:
                if ziduanming[0] in noidziduan.keys():
                    context = tr.xpath('td[2]/text()').extract()
                    if context:
                        if StrUtil.delWhite(ziduanming[0].strip(':')) == "LanguagesRequired":
                            item[noidziduan.get(ziduanming[0])] = re.sub('\W',' ',StrUtil.delWhite(context[0])).encode('utf8')
                        else:
                            item[noidziduan.get(ziduanming[0])] = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(context[0])).encode('utf8')

        # TODO  提取技能经历等数据
        skilldatas = job.xpath('//div[@id="content-main"]/table[2]/tr')

        for i in range(0,len(skilldatas),1):
            name = skilldatas[i].xpath('td[@class="field"]/h5/text()').extract()
            if name:
                if name[0] in textnfo_noid.keys():
                    info = skilldatas[i+1].xpath('td[@class="text"]').xpath('string(.)').extract()
                    item[textnfo_noid.get(name[0])] = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(info[0])).encode('utf8')
                elif "Skills" in name[0]:
                    data = StrUtil.delMoreSpace(StrUtil.delWhiteSpace(skilldatas[i + 1].xpath('td[@class="text"]').xpath('string(.)').extract()[0]))
                    try:
                        item['education'] = re.sub(r'Exp[eé]rience:','',re.search(r'Education(.*?)Exp[e,é]rience:',data,re.I).group(0)).encode('utf8')
                        item['experience'] = re.search(r'Exp[eé]rience(.*?)Langu', data, re.I).group(0).strip('Langu').encode('utf8')
                    except:
                        item['education'] = item['experience'] = data

    def _crawliframe(self,response):
        '''
        UNDP网站中*号岗位页面为嵌套网页
        实际网页在iframe框架中，提取iframe网页中真实页面
        '''
        selector = scrapy.Selector(response)
        link = selector.xpath('//iframe/@src').extract()[0]
        yield Request(url=link,callback=self._crawlhaveid,meta=response.meta,headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Connection": "keep-alive",
            "Cookie": "ExpirePage=https://jobs.partneragencies.net/psc/UNDPP1HRE2/; PS_LOGINLIST=https://jobs.partneragencies.net/UNDPP1HRE2; p1hre2-8250-PORTAL-PSJSESSIONID=TMB5ZmwQvtQrGcvRttShnVM28z3TdJv6!-454263630; PS_TOKEN=AAAAvAECAwQAAQAAAAACvAAAAAAAAAAsAARTaGRyAgBOiQgAOAAuADEAMBQyejPz3FSX5ezsObx1koeyEUlRZAAAAHwABVNkYXRhcHicLcpBCoJQEMbx/1Nx2TncKC97oB2gdBWS7kXKhRAikeAVulOH81MamN/MfAzwNZ4fYFB5v82Inrf6IWcGPiS6Fs0tH+l4KXkyhVy4URyoqLnS0FJyd6RYjmTE0u7m/z2RJ2lx0inP988zKxWUEdw=; SignOnDefault=erecruit.external.dp; ACE-JOBS=R4226155932; PS_TOKENEXPIRE=18_Oct_2017_06:27:34_GMT",
            "Host": "jobs.partneragencies.net",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        })

    def _crawlhaveid(self,response):
        '''
        页面提取器，解析字段
        解析iframe框架页面
        '''

        item = self.initItem()
        item['joburl'] = response.url
        item["description"] = response.meta["describe"]
        item["belong"] = response.meta["suoshu"]
        item["issuedate"] = response.meta["applytime"]
        item['incontinent'] = '北美洲'
        item['alljoburl'] = 'https://jobs.undp.org/cj_view_jobs.cfm'
        item['type'] = '科学研究'
        item['englishname'] = 'UNDP'
        item['chinesename'] = '联合国开发计划署'
        item['url'] = 'http://www.undp.org/'
        item['incountry'] = '美国'
        field = ['Agency', 'Title', 'Job ID', 'Practice Area - Job Family', 'Vacancy End Date', 'Time Left',
                         'Duty Station', 'Education & Work Experience', 'Languages', 'Grade', 'Vacancy Type',
                         'Posting Type',
                         'Bureau', 'Contract Duration', 'Background', 'Duties and Responsibilities', 'Competencies',
                         'Required Skills and Experience',
                         'Disclaimer']
        id2field = {'Agency':'',
                    'Title':'work',
                    'JobID':'',
                    'PracticeAreaJobFamily':'belong',
                    'VacancyEndDate':'ApplicationDeadline',
                    'DutyStation':'Location',
                    'TimeLeft':'',
                    'EducationWorkExperience':'education',
                    'Languages':'language',
                    'Grade':'PostLevel',
                    'VacancyType':'',
                    'PostingType':'',
                    'Bureau':'',
                    'ContractDuration':'contracttime',
                    'Background':'description',
                    'DutiesandResponsibilities':'responsibilities',
                    'Competencies':'skill',
                    'RequiredSkillsandExperience':'experience',
                    'Disclaimer':'addition'}

        selector = scrapy.Selector(response)
        table = selector.xpath("//table[@id='ACE_$ICField30$0']/tr/td")
        tds = [t.strip() for t in table.xpath("string(.)").extract()]
        table2 = selector.xpath("//table[@id='ACE_HRS_JO_PST_DSCR$0']/tr/td")
        tds2 = [t.strip() for t in table2.xpath("string(.)").extract()]
        tds.extend(tds2)
        tds.append('Disclaimer')
        temp = []
        key = 'default'
        value = ''
        try:
            for td in tds:
                if td in field:
                    value = StrUtil.delMoreSpace(''.join(temp).encode('utf-8'))
                    try:
                        if key not in ['JobID','TimeLeft','VacancyType','PostingType','Bureau','Agency']:
                            item[id2field.get(key)] = value
                    except:
                        pass
                    temp = []
                    key = re.sub('[-& ]', '', td.encode('utf-8'))
                else:
                    temp.append(td)
        except:
            logger.error('parser error!')
        self.debugItem(item)
        self.insert(item,spiderName=self.name)
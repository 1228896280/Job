# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
import json
import requests
from scrapy_splash import SplashRequest
from ...allitems.jobitems import AllJobs
import logging.config
logger = logging.getLogger('ahu')

class WHOjobSpider(scrapy.Spider):
    name = "WHOjob"
    def __init__(self):
        logger.debug("开始爬取WHO岗位信息")
        self.preurl = "https://tl-ex.vcdp.who.int/careersection/ex/jobdetail.ftl?job="

    def start_requests(self):
        ur = 'https://tl-ex.vcdp.who.int/careersection/rest/jobboard/searchjobs?lang=en&portal=101430233'
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Connection": "keep-alive",
            "Content-Length": "946",
            "Content-Type": "application/json",
            "Cookie": "locale=en",
            "Host": "tl-ex.vcdp.who.int",
            "Origin": "https://tl-ex.vcdp.who.int",
            "Referer": "https://tl-ex.vcdp.who.int/careersection/ex/jobsearch.ftl",
            "tz": "GMT+08:00",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        data = json.loads('{"multilineEnabled":true,"sortingSelection":\
                {"sortBySelectionParam":"3","ascendingSortingOrder":"false"},\
                "fieldData":{"fields":{"KEYWORD":"","LOCATION":""},\
                "valid":true},"filterSelectionParam":{"searchFilterSelections":[{"id":"POSTING_DATE","selectedValues":[]},\
                {"id":"LOCATION","selectedValues":[]},\
                {"id":"JOB_FIELD","selectedValues":[]},\
                {"id":"JOB_TYPE","selectedValues":[]},\
                {"id":"JOB_SCHEDULE","selectedValues":[]},\
                {"id":"JOB_LEVEL","selectedValues":[]},\
                {"id":"EMPLOYEE_STATUS","selectedValues":[]}]},\
                "advancedSearchFiltersSelectionParam":{"searchFilterSelections":[{"id":"ORGANIZATION","selectedValues":[]},\
                {"id":"LOCATION","selectedValues":[]},\
                {"id":"JOB_FIELD","selectedValues":[]},\
                {"id":"JOB_NUMBER","selectedValues":[]},\
                {"id":"URGENT_JOB","selectedValues":[]},\
                {"id":"EMPLOYEE_STATUS","selectedValues":[]},\
                {"id":"JOB_SCHEDULE","selectedValues":[]},\
                {"id":"JOB_TYPE","selectedValues":[]},\
                {"id":"JOB_LEVEL","selectedValues":[]}]},"pageNo":2}')

        for i in range(1, 6, 1):
            '''
            post请求每个岗位页面，获取json格式的返回信息
            >>>response:
                       link,work,Location,PostLevel,ContractualArrangement,ClosingDate
            '''
            data["pageNo"] = i
            post_data = json.dumps(data)
            response = requests.post(ur, data=post_data, headers=headers)
            result = json.loads(response.text)
            for everydata in result["requisitionList"]:
                work = everydata["column"][0]
                num = everydata["column"][1]
                Location = everydata["column"][2].strip('[').strip(']').strip('"')
                PostLevel = everydata["column"][3]
                ContractualArrangement = everydata["column"][4]
                ClosingDate = everydata["column"][5]
                # todo 使用splash渲染每个请求页面，加载js脚本
                yield SplashRequest(url=self.preurl + num,
                              callback=self.parseWHOjob,
                              meta={'work':work,
                                    'Location':Location,
                                    'PostLevel':PostLevel,
                                    'ContractualArrangement':ContractualArrangement,
                                    'ClosingDate':ClosingDate},
                                args={'wait': 2})

    def parseWHOjob(self,response):
        '''
        页面提取器，解析字段
        '''
        item = self.setitem(response)
        selector = scrapy.Selector(response)

        # 爬取合同期限
        ContractdurationXpath = '//div[@class="editablesection"]/div[@id="requisitionDescriptionInterface.ID1489.row1"]/' \
                                'span[@id="requisitionDescriptionInterface.ID1522.row1"]/text()'
        Contractduration = response.xpath(ContractdurationXpath).extract()
        item["contracttime"] = Contractduration[0] if Contractduration else ""

        # 爬取主要地点
        PrimaryLocationXpath = '//div[@class="editablesection"]/div[@id="requisitionDescriptionInterface.ID1653.row1"]/' \
                               'span[@id="requisitionDescriptionInterface.ID1696.row1"]/text()'
        PrimaryLocation = response.xpath(PrimaryLocationXpath).extract()
        item["Location"] += PrimaryLocation[0] if Contractduration else ""

        # 爬取工作公告
        JobPostingXpath = '//div[@class="editablesection"]/div[@id="requisitionDescriptionInterface.ID1549.row1"]/' \
                          'span[@id="requisitionDescriptionInterface.reqPostingDate.row1"]/text()'
        JobPosting = selector.xpath(JobPostingXpath).extract()
        item["issuedate"] = JobPosting[0] if JobPosting else ""

        # 爬取所在组织
        OrganizationXpath = '//div[@class="editablesection"]/div[@id="requisitionDescriptionInterface.ID1753.row1"]/' \
                            'span[@id="requisitionDescriptionInterface.ID1796.row1"]/text()'
        Organization = selector.xpath(OrganizationXpath).extract()
        item["belong"] = Organization[0] if Organization else ""

        # 爬取是否要求全职
        ScheduleXpath = '//div[@class="editablesection"]/div[@id="requisitionDescriptionInterface.ID1803.row1"]/' \
                        'span[@id="requisitionDescriptionInterface.ID1846.row1"]/text()'
        Schedule = selector.xpath(ScheduleXpath).extract()
        item["full_time"] = Schedule[0] if Schedule else ""

        data = ' '.join(selector.xpath('//div[@id="requisitionDescriptionInterface.ID1865.row1"]').xpath('string(.)').extract()[0].split())

        if 'DESCRIPTION OF DUTIES' in data:
            info = data.split('DESCRIPTION OF DUTIES')
            item['description'] = info[0]
        elif 'Summary of Assigned Duties:' in data:
            info = data.split('Summary of Assigned Duties:')
            item['description'] = info[0]
        else:
            info = data

        if 'REQUIRED QUALIFICATIONS' in info[-1]:
            info2 = info[-1].split('REQUIRED QUALIFICATIONS')
            item['responsibilities'] = info2[0]
        elif 'Recruitment Profile Competencies:' in info[-1]:
            info2 = info[-1].split('Recruitment Profile Competencies:')
            item['responsibilities'] = info2[0]
        else:
            info2 = info

        if 'Education Essential:' in info2[-1]:
            info3 = info2[-1].split('Education Essential:')
        elif 'Education:' in info2[-1]:
            info3 = info2[-1].split('Education:')
        elif 'Education Qualifications' in info2[-1]:
            info3 = info2[-1].split('Education Qualifications')
            item['skll'] = info3[0]
        else:
            info3 = info2

        if 'Experience Essential:' in info3[-1]:
            info4 = info3[-1].split('Experience Essential:')
            item['education'] = info4[0]
        elif 'Experience:' in info3[-1]:
            info4 = info3[-1].split('Experience:')
            item['education'] = info4[0]
        else:
            info4 = info3

        if 'Skills' in info4[-1]:
            info5 = info4[-1].split('Skills')
            down = ''
            for text in info5[1:]:
                down += text
            info5[1] = down
            count = len(info5[2:])
            while count:
                info5.pop()
                count -= 1
            item['experience'] = info5[0]
        elif 'SKILLS:' in info4[-1]:
            info5 = info4[-1].split('SKILLS:')
            item['experience'] = info5[0]
        else:
            info5 = info4
        if 'Language' in info5[-1]:
            info6 = info5[-1].split('Use of Language Skills')
            item['skill'] = info6[0]
        else:
            info6 = info5
        if 'REMUNERATION' in info6[-1]:
            info7 = info6[-1].split('REMUNERATION')
            item['language'] = info7[0]
        elif 'Other Skills(e.g.IT)' in info6[-1]:
            info7 = info6[-1].split('Other Skills(e.g.IT)')
            item['addition'] = info7[-1]
        else:
            info7 = info6
        if 'ADDITIONAL INFORMATION' in info7[-1]:
            info8 = info7[-1].split('ADDITIONAL INFORMATION')
            item['treatment'] = info8[0]
            item['addition'] = info8[-1]
        yield item

    def setitem(self,response):
        '''
        初始化WHO的item
        '''
        item = AllJobs()
        item["englishname"] = "WHO"
        item["chinesename"] = "世界卫生组织"
        item["incontinent"] = "欧洲"
        item["incountry"] = "瑞士"
        item["type"] = "卫生"
        item["url"] = "http://www.who.int/en/"
        item["alljoburl"] = "https://tl-ex.vcdp.who.int/careersection/ex/jobsearch.ftl#"
        item["joburl"] = response.url
        item["work"] = response.meta["work"]
        item["Location"] = response.meta["Location"]
        item["PostLevel"] = response.meta["PostLevel"]
        item['ApplicationDeadline'] = response.meta["ClosingDate"]
        item['description'] = ''
        item['reference'] = ''
        item['issuedate'] = ''
        item['responsibilities'] = ''
        item['skill'] = ''
        item['belong'] = ''
        item['TypeofContract'] = ''
        item['language'] = ''
        item['contracttime'] = ''
        item['ExpectedDurationofAssignment'] = ''
        item['linkman'] = ''
        item['full_time'] = ''
        item['treatment'] = ''
        item['education'] = ''
        item['addition'] = ''
        item['experience'] = ''
        return item


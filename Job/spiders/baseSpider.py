# coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import logging.config
from Job.allitems.jobitems import AllJobs
from scrapy.spiders import Spider
from ..pipelines.pipeline import JobPipeline
logger = logging.getLogger('ahu')

class baseSpider(Spider):

    name = 'baseSpider'

    def __init__(self, *a, **kw):
        super(baseSpider, self).__init__(*a, **kw)
        self.jobPipeline = JobPipeline()

    def initItem(self):
        '''
        初始化全部字段
        '''
        item = AllJobs()
        item = {k:'' for k in item.fields}
        return item

    def debugItem(self,item):
        '''
       调试输出item
        '''
        for k,v in item.items():
            logger.debug('%s>>>%s'%(k,v))

    def insert(self,item,spiderName):
        self.jobPipeline.process_item(item=item,spiderName=spiderName)

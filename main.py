# -*- coding: utf-8 -*-

'''
    基于scrapydo的爬虫启动文件
'''
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapydo
import logging.config
from Job.utils.Util import FileUtil
from Job import settings

'''
    若日志输出文件路径不存在，创建日志输出文件路径
    默认在c盘log文件夹下
    >>>settings.LOGPATH
    >>>c:\\log
'''
if os.path.exists(settings.LOGPATH) == False:
    os.makedirs(settings.LOGPATH)
logging.config.fileConfig(FileUtil().getLogConfigPath())
logger = logging.getLogger('ahu')

from Job.spiders.jobSpider.crawlUNDPjobs import UNDPjobSpider
from Job.spiders.jobSpider.crawlCERNjobs import CERNjobsSpider
from Job.spiders.jobSpider.crawlITERjobs import ITERJobSpider
from Job.spiders.jobSpider.crawlMOHRSSjobs import MOHRSSJobSpider
from Job.spiders.jobSpider.crawlOECDjobs import OECDJobSpider
from Job.spiders.jobSpider.crawlUNIDOjobs import UNIDOjobLink
from Job.spiders.jobSpider.crawlUNUjobs import UNUjobSpider
from Job.spiders.jobSpider.crawlWHOjobs import WHOjobSpider
from Job.spiders.jobSpider.crawlWIPOjobs import WIPOjobSpider
scrapydo.setup()

class StartScrapySpider(object):
    def __init__(self,type):
        self.type = type
        self.start()

    def start(self):
        '''使用scrapydo启动爬虫
            如有新增爬虫需要启动，可在spiders中添加'''
        if self.type == 'job':
            logger.debug("进行岗位准备")
            spiders = [
                # UNDPjobSpider,
                # CERNjobsSpider,
                # ITERJobSpider,
                MOHRSSJobSpider, #唯一国内网站，测试ip效果较好
                # OECDJobSpider,
                # UNIDOjobLink,
                # UNUjobSpider,
                # WHOjobSpider,
                # WIPOjobSpider,
            ]
        else:
            spiders = []

        for spider in spiders:
            scrapydo.run_spider(spider_cls=spider)

if __name__ == "__main__":
    startScrapySpider = StartScrapySpider('job')
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
import re
import time
from selenium import webdriver
from scrapy.http import Request
from scrapy_splash import SplashRequest
import logging.config
from ..baseSpider import baseSpider
from ...utils.Util import StrUtil
logger = logging.getLogger('ahu')
class UNESCOjobSpider(baseSpider):
    name = "UNESCOjob"
    start_urls = []

    def __init__(self,*a, **kw):
        super(UNESCOjobSpider, self).__init__(*a, **kw)
        # self.driver = webdriver.PhantomJS()
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

    def start_requests(self):
        self.driver.get("https://careers.unesco.org/careersection/1/joblist.ftl?lang=en")
        time.sleep(3)
        click_text = "HR ASSISTANT"
        self.driver.find_element_by_link_text(click_text).click()
        time.sleep(3)
        self.parseJob(self.driver.page_source)

        while True:
            self.driver.find_element_by_id("requisitionDescriptionInterface.pagerDivID765.Next").click()
            time.sleep(5)
            self.parseJob(self.driver.page_source)

    def parseJob(self,response):
        selector = scrapy.Selector(response)
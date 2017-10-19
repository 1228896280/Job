# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class AllLeaders(scrapy.Item):
    '''
    定义领导人字段
    '''
    name = scrapy.Field()         #姓名
    work = scrapy.Field()         #职位
    url = scrapy.Field()          #领导人连接
    englishname = scrapy.Field()  #机构
    resume = scrapy.Field()       #简历
    department = scrapy.Field()   #部门



# -*- coding: utf-8 -*-

'''
    scrapy数据存储，接受爬取传递的item并持久化入mysql
'''
from twisted.enterprise import adbapi
from mysqlDB import myaqlSave
from ..allitems.jobitems import AllJobs
from ..allitems.leaderitems import AllLeaders

class JobPipeline(object):
    # TODO 初始化Mysql
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        name = settings['DB_SERVER']
        dbargs = settings['DB_CONNECT']
        dbpool = adbapi.ConnectionPool(name, **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        if isinstance(item, AllLeaders):
            self.dbpool.runInteraction(myaqlSave().insertleaders, item)
        if isinstance(item, AllJobs):
            self.dbpool.runInteraction(myaqlSave().insertjobs, item)

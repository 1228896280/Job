# -*- coding: utf-8 -*-

'''
    scrapy数据存储，接受爬取传递的item并持久化入mysql
'''
from twisted.enterprise import adbapi
from mysqlDB import myaqlSave
from ..allitems.jobitems import AllJobs
from ..allitems.leaderitems import AllLeaders
import logging.config
import pymysql
from .. import settings
logger = logging.getLogger('ahu')

class JobPipeline(object):
    # TODO 初始化Mysql
    def __init__(self):
        self.myaqlsave = myaqlSave()
        self.conn = pymysql.connect(**settings.MYSQLDB_CONNECT)
        self.cursor = self.conn.cursor()
        try:
            self.conn.select_db(settings.DB)
        except:
            self.create_database(settings.DB)
            self.conn.select_db(settings.DB)
            self.init()

    def init(self):
        # 创建商品抓取记录表
        jobCommand = ('DROP TABLE IF EXISTS `alljob`;'
                    'CREATE TABLE `alljob` ('
                      '`英文缩写` varchar(20) DEFAULT NULL,'
                      '`中文名称` varchar(80) DEFAULT NULL,'
                      '`所属洲` varchar(40) DEFAULT NULL,'
                      '`所在地` varchar(100) DEFAULT NULL,'
                      '`分类` varchar(40) DEFAULT NULL,'
                      '`主页url` varchar(80) DEFAULT NULL,'
                      '`招聘网址` varchar(80) DEFAULT NULL,'
                      '`岗位url` varchar(150) NOT NULL,'
                      '`岗位名称` varchar(300) NOT NULL,'
                      '`工作地点` varchar(300) DEFAULT NULL,'
                      '`职级` varchar(50) DEFAULT NULL,'
                      '`发布日期` varchar(150) DEFAULT NULL,'
                      '`截止日期` varchar(150) DEFAULT NULL,'
                      '`职位介绍` text,'
                      '`职能` text,'
                      '`技能` text,'
                      '`组织机构` text,'
                      '`包工方式` text,'
                      '`语言` text,'
                      '`初始合同时间` text,'
                      '`预计工作时间` varchar(200) DEFAULT NULL,'
                      '`联系人` text,'
                      '`是否全职` varchar(50) DEFAULT NULL,'
                      '`待遇` text,'
                      '`教育背景` text,'
                      '`附加的` text,'
                      '`工作经历` text,'
                      '`参考` text,'
                      'PRIMARY KEY (`岗位名称`(100),`岗位url`(100))'
                    ') ENGINE=InnoDB DEFAULT CHARSET=utf8;')

        leaderCommand = ('DROP TABLE IF EXISTS `allleader`;'
                            'CREATE TABLE `allleader` ('
                              '`姓名` varchar(50) NOT NULL DEFAULT "",'
                              '`职位` varchar(100) DEFAULT "",'
                              '`链接` varchar(255) NOT NULL DEFAULT "",'
                              '`机构` varchar(50) DEFAULT "",'
                              '`简历` text,'
                              '`部门` varchar(255) DEFAULT "",'
                              'PRIMARY KEY (`姓名`,`链接`)'
                            ') ENGINE=InnoDB DEFAULT CHARSET=utf8;')

        self.create_table(jobCommand)
        self.create_table(leaderCommand)

    def create_database(self, database_name):
        try:
            command = 'CREATE DATABASE IF NOT EXISTS %s DEFAULT CHARACTER SET \'utf8\' ' % database_name
            self.cursor.execute(command)
        except Exception, e:
            logger.warning('创建数据库异常:%s' % str(e))

    def create_table(self, command):
        try:
            self.cursor.execute(command)
            self.conn.commit()
        except Exception, e:
            logger.warning('创建表异常:%s' % str(e))

    def process_item(self, item, spider):
        if isinstance(item, AllLeaders):
            self.myaqlsave.insertleaders(self.cursor,self.conn,item)
        if isinstance(item, AllJobs):
            self.myaqlsave.insertjobs(self.cursor,self.conn,item)

# -*- coding: utf-8 -*-

import logging.config
logger = logging.getLogger('ahu')

class myaqlSave(object):
    '''
        item存储
    '''
    def __init__(self):
        pass
    def insertleaders(self,tx,conn,item):
        try:
            tx.execute('insert into allleader(姓名,职位,链接,机构,简历,部门)values(%s,%s,%s,%s,%s,%s)',
                       (item['name'],item['work'],item['url'],item['englishname'],item['resume'],item['department']))
            conn.commit()

        except Exception as e:
            # logger.debug(item)
            logger.error("存储领导人数据失败" + str(e))

    def insertjobs(self, tx,conn,item):
        content = 'insert into  岗位(英文缩写,中文名称,岗位url,岗位名称,工作地点,职级,发布日期,截止日期,职位介绍,职能,技能,组织机构,语言,初始合同时间,是否全职,待遇,教育背景,附加的,工作经历)'
        type = 'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        try:
            tx.execute(content+type,(item["englishname"],item["chinesename"],item['joburl'],item['work'],item['Location'],item['PostLevel'],
                                     item['issuedate'],item['ApplicationDeadline'],item['description'],item['responsibilities'],item['skill'],
                                     item['belong'],item['language'],item['contracttime'],item['full_time'],item['treatment'],item['education'],
                                     item['addition'],item['experience']))
            conn.commit()
        except Exception as e:
            logger.debug(item)
            logger.error("存储岗位数据失败" + str(e))

    def insertorg(self,tx,conn,item):
        try:
            tx.execute('insert into 组织(英文缩写,中文名称,所属洲,所在地,分类,主页url,招聘网址url)values(%s,%s,%s,%s,%s,%s,%s)',
                       (item["englishname"],item["chinesename"],item["incontinent"],item["incountry"],item["type"],
                        item["url"],item["alljoburl"]))
            conn.commit()
        except Exception as e:
            pass

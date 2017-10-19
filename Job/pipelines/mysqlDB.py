# -*- coding: utf-8 -*-

import logging.config
logger = logging.getLogger('ahu')

class myaqlSave(object):
    '''
        item存储
    '''
    def __init__(self):
        pass
    def insertleaders(self,tx,item):
        try:
            tx.execute('insert into allleader(姓名,职位,链接,机构,简历,部门)values(%s,%s,%s,%s,%s,%s)',(item['name'],item['work'],item['url'],
                                                                                            item['englishname'],item['resume'],item['department']))

        except Exception as e:
            # logger.debug(item)
            logger.error("存储领导人数据失败" + str(e))

    def insertjobs(self, tx, item):
        content = 'insert into alljob(英文缩写,中文名称,所属洲,所在地,分类,主页url,招聘网址,岗位url,岗位名称,工作地点,职级,发布日期,截止日期,职位介绍,职能,技能,组织机构,包工方式,语言,初始合同时间,预计工作时间,联系人,是否全职,待遇,教育背景,附加的,工作经历,参考)'
        type = 'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        try:
            tx.execute(content+type,(item["englishname"],item["chinesename"],item["incontinent"],item["incountry"],item["type"],
                        item["url"],item["alljoburl"],item['joburl'],item['work'],item['Location'],item['PostLevel'],item['issuedate'],
                        item['ApplicationDeadline'],item['description'],item['responsibilities'],item['skill'],item['belong'],
                        item['TypeofContract'],item['language'],item['contracttime'],item['ExpectedDurationofAssignment'],
                        item['linkman'],item['full_time'],item['treatment'],item['education'],item['addition'],
                        item['experience'],item['reference']))
        except Exception as e:
            # logger.debug(item)
            logger.error("存储岗位数据失败" + str(e))

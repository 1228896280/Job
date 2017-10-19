开源爬虫
=================================

基于scrapy + splash的开源爬虫并在爬取中动态维护ip，解决ip和js问题
------------------------------------------------------------------

项目详情
========
爬虫主要爬取一些国际组织的招聘岗位信息，解析一些招聘要求。其中只有MOHRSSjob为国内站点，测试动态ip的使用情况，效果较好。部分网站使用了splash进行解析，也写了phantomjs的解析示例。
若使用phantomjs需下载phantomjs.exe并放置于Script下

开发环境
=================================

* Python 2.7
* scrapy
* scrapydo
* scrapy-splash
* selenium
* mysql
* bs4

### 下载安装

* 下载源码:

```shell
git clone git@github.com:18010927657/Job.git

或者直接到https://github.com/18010927657/Job 下载zip文件
```

* 安装依赖:

```shell
pip install -r requirements.txt
```

* 配置settings:

```shell
# settings 为scrapy项目配置文件
# 配置DB
DB_CONNECT		  #修改mysql连接信息


# 配置 SPLASH_URL
本爬虫使用splash渲染js脚本，安装参考
##### [splash安装](http://www.jianshu.com/p/4052926bc12c)
....

```

* 启动:

```shell
# 如果你的依赖已经安全完成并且具备运行条件,可以直接在Job下运行main.py
# 到Run目录下:
>>>python main.py

```

数据库
=================================

1.alljob<br />
```sql
DROP TABLE IF EXISTS `alljob`;
CREATE TABLE `alljob` (
  `英文缩写` text,
  `中文名称` text,
  `所属洲` text,
  `所在地` text,
  `分类` text,
  `主页url` text,
  `招聘网址` text,
  `岗位url` text NOT NULL,
  `岗位名称` text NOT NULL,
  `工作地点` text,
  `职级` text,
  `发布日期` text,
  `截止日期` text,
  `职位介绍` text,
  `职能` text,
  `技能` text,
  `组织机构` text,
  `包工方式` text,
  `语言` text,
  `初始合同时间` text,
  `预计工作时间` text,
  `联系人` text,
  `是否全职` text,
  `待遇` text,
  `教育背景` text,
  `附加的` text,
  `工作经历` text,
  `参考` text,
  PRIMARY KEY (`岗位名称`(100),`岗位url`(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

### 问题反馈

　　任何问题欢迎在[Issues](https://github.com/18010927657/Job/issues) 中反馈，也可以发邮件到我的邮箱liuy_anhui@163.com。我看到会立即反馈

　　你的反馈会让此项目变得更加完美。


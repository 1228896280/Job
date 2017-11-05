# -*- coding: utf-8 -*-
'''
	脚本处理
'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re,os
import logging.config

class FileUtil(object):
	def __init__(self):
		print "FileUtil ok"
		'''路径设置工具'''

	def cur_file_dir(self):
		"""
		获取脚本文件的当前路径
       """
		# 获取脚本路径
		path = sys.path[0]
		# 判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
		if os.path.isdir(path):
			return path
		elif os.path.isfile(path):
			return os.path.dirname(path)

	def getLogConfigPath(self):
		"""
        获取logging配置文件的路径
        """
		rootFolder = "Job"
		logPath = self.cur_file_dir().split(rootFolder, 1)[0] + rootFolder + "/Job/logging.ini"
		# print logPath
		return logPath

logging.config.fileConfig(FileUtil().getLogConfigPath())
logger = logging.getLogger('ahu')
class StrUtil(object):
	def __init__(self):
		logger.debug("StrUtil ok")
		'''字符串处理工具'''

	@staticmethod
	def delWhiteSpace(msg):
		'''
		将字符串中的空白符换为空格
		'''
		pattern = re.compile('\\s+')
		return (re.sub(pattern, ' ', msg)).strip()

	@staticmethod
	def delMoreSpace(msg):
		'''
		将字符串的多个连续空格转换成一个
		'''
		return ' '.join(msg.split())

	@staticmethod
	def delWhite(msg):
		'''
        删除字符串中的空白符
        '''
		pattern = re.compile('\\s+')
		return (re.sub(pattern, '', msg)).strip()

	@staticmethod
	def isEmpty(msg):
		'''
		判断字符串是否为空
		'''
		return msg and msg.strip()

	@staticmethod
	def completeURL(prefix, url):
		'''
		判断URL是否包含prefix并补全
		'''
		index = prefix.rfind('/')
		url = prefix[0:index + 1] + url
		return url
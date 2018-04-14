#! /usr/bin/python
# coding=utf-8

import sys
import os
dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(dir_path)))
# reload(sys)
# sys.setdefaultencoding("utf-8")
# sys.path.append('/Users/mrs/Desktop/project/mytest/lagou/lagou_spider')

import gevent
import time
import json

from gevent import monkey
from gevent.pool import Pool
monkey.patch_all()

from lxml import etree
from lagou_spider.database import db_operate
from lagou_spider.util import request
from lagou_spider.util import log
from lagou_spider.util import handle
from common import send_email
from lagou_spider import config

class LagouBase(object):
	"""
	拉钩spider的基类
	"""

	start_url = 'https://www.lagou.com/'
	except_count = 0
	request_count = 0
	urls = []

	def __init__(self):
		self.lagou_db = db_operate.LagouDatebase()
		self.logger = log.logger
		self.count = 0
		self.email_server = send_email.SendEmail(from_name=config.from_name)
		self.pool = Pool(100)

	def start_spider(self):
		"""
			爬虫开始
			: 获取所有 "技术" 相关的职位的url
		"""
		self.count = 0
		self.request_count = 0
		self.except_count = 0
		self.urls = []
		start_time = time.time()
		response = request.get(self.start_url)
		self.request_count += 1
		if response:
			cookies = response.cookies
			html = etree.HTML(response.content)
			menu = html.xpath("//div[@class='menu_sub dn']")[0]
			positions_dict = {}
			types = menu.xpath("dl")
			for item in types:
				type_name = item.xpath("dt/span/text()")[0]
				# print(type_name)
				positions_dict[type_name] = {}
				positions = item.xpath("dd/a")
				for position in positions[0:1]:
					position_name = position.text
					position_url = position.xpath('@href')[0]
					positions_dict[type_name][position_name] = position_url
					position_data = {'first_type': position_name, 'second_type': type_name}
					# self.get_positons_list(position_url, position_data, cookies)
					g = gevent.spawn(self.get_positons_list,*(position_url, position_data, cookies))
					self.pool.add(g)
		else:
			self.except_count += 1
		self.pool.join()
		self.send_email(start_time)

	def get_positons_list(self, url, item, cookies):
		"""获取不同职位类别的列表页"""
		pass

	def get_positions_urls(self, url, item, cookies=None):
		"""获取列表页的urls"""
		pass

	def get_position_detail(self, url, position, cookies=None):
		"""获取详情页的数据"""
		pass

	# 计数器
	def generate_counter(func):
		"""
		计数器
		"""
		# cont = [0]
		def inner(*args, **kwargs):
			result = func(*args, **kwargs)
			if result:
				# cont[0] = cont[0] + 1
				args[0].count += 1
				args[0].logger.info('第%s条数据插入成功！' % args[0].count)
			return result

		return inner

	@generate_counter
	def save_infos(self, data):
		"""
		作用：保存数据
		"""
		# 插入前判断url是否存在
		if self.lagou_db.isexist_url(data['url']):
			self.logger.debug('此url %s 已经存在！' % data['url'])
			return
		
		data['publish_date'] = str(data['publish_date'])
		self.logger.info('===%s===\n%s' % (data['url'],json.dumps(data,ensure_ascii=False,indent=2)))
		t = self.lagou_db.insert_position(data)
		# print('+++++++++%s++++++'%data)
		if not t:
			self.logger.error('数据插入失败!')
		return t

	def send_email(self, start_time):
		"""发送邮件"""
		end_time = time.time()
		run_time = (end_time - start_time)/60
		text = '%s \n运行: %.3f minutes，共添加 %s 条数据' % (handle.get_datetime(start_time), run_time, self.count)
		text += '\nrequest_count:%d, except_count:%d' % (self.request_count, self.except_count)
		except_rate = float(self.except_count) / self.request_count * 100
		self.logger.info(text)
		if self.count == 0:
			subject = '拉钩网-数据爬取-异常'
			text += '\n 爬取数据是 0 条，爬虫可能出现异常，请查看服务器日志！'
		elif except_rate > 35:
			subject = '拉勾网-数据爬取-异常'
			text += '\n 请求的异常率为%.2f (%s/%s)，可能出现了反爬，请查看服务器了解详情。' \
					% (except_rate, self.except_count, self.request_count)
		else:
			subject = '拉钩网-日常数据-爬取信息'
		result = self.email_server.send_email_text(to_addrs=config.to_addrs, msg=text, subject_test=subject)
		if not result == {}:
			self.logger.error('发送邮件失败:%s' % result)
			

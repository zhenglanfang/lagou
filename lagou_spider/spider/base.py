#! /usr/bin/python
# coding=utf-8

import sys


sys.path.append('/Users/mrs/Desktop/project/mytest/lagou/lagou_spider')

import gevent

from gevent import monkey
from gevent.pool import Pool
monkey.patch_all()

from lxml import etree
from database import db_operate
from util import request


class LagouBase(object):
	"""
	拉钩spider的基类
	"""

	start_url = 'https://www.lagou.com/'

	def __init__(self):
		pass

	def start_spider(self):
		"""
			爬虫开始
			: 获取所有 "技术" 相关的职位的url
		"""
		response = request.get(self.start_url)
		if response:
			cookies = response.cookies
			html = etree.HTML(response.content)
			menu = html.xpath("//div[@class='menu_sub dn']")[0]
			positions_dict = {}
			types = menu.xpath("dl")
			pool = Pool(10)
			for item in types:
				type_name = item.xpath("dt/span/text()")[0]
				# print(type_name)
				positions_dict[type_name] = {}
				positions = item.xpath("dd/a")
				for position in positions:
					position_name = position.text
					position_url = position.xpath('@href')[0]
					positions_dict[type_name][position_name] = position_url
					position_data = {'first_type': position_name, 'second_type': type_name}
					# self.get_positons_list(position_url, position_data, cookies)
					g = gevent.spawn(self.get_positons_list,*(position_url, position_data, cookies))
					pool.add(g)
			pool.join()
		# return positions_dict

	def get_positons_list(self, url, item, cookies):
		"""获取不同职位类别的列表页"""
		pass

	def get_positions_urls(self, response, item, cookies):
		"""获取列表页的urls"""
		pass

	def get_position_detail(self, response, position):
		"""获取详情页的数据"""
		pass

	# 计数器
	def generate_counter(func):
		"""
		计数器
		"""
		cont = [0]

		def inner(*args, **kwargs):
			result = func(*args, **kwargs)
			if result:
				cont[0] = cont[0] + 1
				print '第%s条数据插入成功！' % (cont[0])
			return result

		return inner

	@generate_counter
	def save_infos(self, data):
		"""
		作用：保存数据
		"""
		# 插入前判断url是否存在
		if db_operate.isexist_url(data['url']):
			print('此url %s 已经存在！' % data['url'])
			return

		t = db_operate.insert_position(data)
		# print('+++++++++%s++++++'%data)
		if not t:
			print('数据插入失败!')
		return t

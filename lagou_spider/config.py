#! /usr/bin/python
# coding=utf-8

import os
import logging

# mysql 数据库
MYSQL_PROD = "mysql+pymysql://root:root@127.0.0.1:3306/lagou?charset=utf8"

# 日志
log_level = logging.INFO
log_name = 'lagou_spider'
log_path = os.path.join(os.path.dirname(__file__), 'log/lagou_spider.log')

# 调试模式
debug = False

# 邮件
from_name = '拉钩网数据爬取中心'
to_addrs = [('我', '13849182150@163.com')]

# 项目根目录
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))






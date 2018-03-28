#! usr/bin/python
# coding=utf-8
import sys
sys.path.append('/Users/mrs/Desktop/project/mytest/lagou')

import logging
import warnings

from lagou_spider import config
warnings.filterwarnings("ignore")


class Log(object):
	"""docstring for Log"""

	def __init__(self, level, log_name=None):
		super(Log, self).__init__()
		self.logger = logging.getLogger(log_name)
		self._level = level
		self.logger.setLevel(self._level)
		self._formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")

	def print_console(self, level=logging.DEBUG):
		ch = logging.StreamHandler()
		ch.setLevel(level)
		ch.setFormatter(self._formatter)
		self.logger.addHandler(ch)
		return self.logger

	def save_file(self, log_path, level=logging.INFO):
		fh = logging.FileHandler(log_path, mode='a')
		fh.setLevel(level)
		fh.setFormatter(self._formatter)
		self.logger.addHandler(fh)
		return self.logger


def log_init():
	logger = Log(config.log_level, config.log_name)
	if config.debug:
		return logger.print_console(level=config.log_level)
	else:
		return logger.save_file(config.log_path)


logger = log_init()

if __name__ == '__main__':

	"""打印日志到控制台同时保存到文件中"""
	log = Log(config.log_level, config.log_name)
	log.print_console(logging.DEBUG)
	LOG = log.save_file(config.log_path, logging.DEBUG)
	LOG.debug('this is a logger debug message')
	LOG.info('this is a logger info message')
	LOG.warning('this is a logger warning message')
	LOG.error('this is a logger error message')
	LOG.critical('this is a logger critical message')
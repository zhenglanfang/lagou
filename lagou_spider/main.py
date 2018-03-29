#! /usr/bin/python
# coding=utf-8

import schedule
import time

from spider import lagou
from spider import real_time
from lagou_spider.util import log


def main():
	log.logger.info('开始~~~')
	all_lagou = lagou.AllLagou()
	real_lagou = real_time.RealTime()
	# schedule.every().seconds.do(all_lagou.start_spider)
	schedule.every().day.at('14:50').do(real_lagou.start_spider)
	schedule.every().day.at('23:40').do(real_lagou.start_spider)
	schedule.every(3).days.at('22:00').do(all_lagou.start_spider)
	while True:
		schedule.run_pending()
		time.sleep(20)


if __name__ == '__main__':
	main()
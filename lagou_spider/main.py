#! /usr/bin/python

import schedule
import time

from spider import lagou
from spider import real_time


def main():
	all_lagou = lagou.AllLagou()
	real_lagou = real_time.RealTime()
	schedule.every(5).hours.at('8:50').do(real_lagou.start_spider)
	schedule.every(3).days.at('22:00').do(all_lagou.start_spider)
	while True:
		schedule.run_pending()
		time.sleep(20)


if __name__ == '__main__':
	main()
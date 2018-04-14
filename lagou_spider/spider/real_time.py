#! /usr/bin/python
# coding=utf-8

import sys
import os
dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(dir_path)))
# reload(sys)
# sys.setdefaultencoding("utf-8")

import time
import random
import gevent
import copy

from lxml import etree
from lagou_spider.util import request
from lagou_spider.util import handle
from lagou_spider.spider.base import LagouBase

# form_data = {
#     'first':'false',
#     'pn':'3',
#     'kd':'ios',
# }


class RealTime(LagouBase):
    """爬取当天的数据"""

    second_url = 'https://www.lagou.com/jobs/list_%s?px=new&city=全国'
    job_url = 'https://www.lagou.com/jobs/%s.html'
    post_url = 'https://www.lagou.com/jobs/positionAjax.json?px=new&needAddtionalResult=false&isSchoolJob=0'
    logo = 'https://www.lgstatic.com/thumbnail_300x300/%s'

    def __init__(self):
        super(RealTime, self).__init__()

    # 获取职位列表页
    def get_positons_list(self, url, item, cookies):
        self.request_count += 1
        response = request.get(url, cookies=cookies)
        if response:
            cookies = response.cookies
        else:
            self.except_count += 1
        self.get_new_list(response, item, cookies)

    # 获取最新的职位列表
    def get_new_list(self, response, item, cookies):
        item = copy.deepcopy(item)
        if response:
            # new_url = html.xpath("//div[@class='item order']/a[2]/@href")
            new_url = self.second_url % (item['first_type'])
            response = request.get(url=new_url, cookies=cookies)
            self.request_count += 1
            if response:
                referer = response.url
                html = etree.HTML(response.content)
                page_num = html.xpath("//span[@class='span totalNum']/text()")
                page_num = int(page_num[0]) if page_num else 1
                for num in range(1, page_num + 1):
                    g = gevent.spawn(self.get_positions_list, num, item, referer, cookies)
                    self.pool.add(g)
                    # self.get_positions_list(num, item, referer, cookies)
                    # form_data = {
                    #     'first': 'false',
                    #     'pn': str(num),
                    #     'kd': item['first_type'],
                    # }
                    # headers = {
                    #     'Referer': referer,
                    # }
                    # # 如果请求失败，重新请求
                    # for i in range(5):
                    #     time.sleep(random.randint(1, 3))
                    #     response = request.post(url=self.post_url, data=form_data, headers=headers, cookies=cookies)
                    #     try:
                    #         result = response.json(encoding='utf-8')
                    #     except Exception as e:
                    #         self.logger.error(e.message)
                    #     else:
                    #         if result.get('success'):
                    #             result = self.get_positions_urls(result, item, cookies=response.cookies)
                    #             if not result:
                    #                 return
                    #             break
                    #         else:
                    #             self.logger.error('%s %s %s' % (self.post_url, form_data, response.text))
            else:
                self.except_count += 1

    def get_positions_list(self, num, item, referer, cookies):
        item = copy.deepcopy(item)
        form_data = {
            'first': 'false',
            'pn': str(num),
            'kd': item['first_type'],
        }
        headers = {
            'Referer': referer,
        }
        # 如果请求失败，重新请求
        for i in range(5):
            time.sleep(random.randint(1, 3))
            response = request.post(url=self.post_url, data=form_data, headers=headers, cookies=cookies)
            self.request_count += 1
            try:
                result = response.json(encoding='utf-8')
            except Exception as e:
                self.except_count += 1
                self.logger.error(e.message)
            else:
                if result.get('success'):
                    result = self.get_positions_urls(result, item, cookies=response.cookies)
                    if not result:
                        return
                    break
                else:
                    self.logger.error('%s %s %s' % (self.post_url, form_data, response.text))

    # 获取列表页的urls
    def get_positions_urls(self, result, item, cookies):
        item = copy.deepcopy(item)
        content = result.get('content')
        if content:
            if content.get('positionResult'):
                positions = content.get('positionResult').get('result')
                for position in positions:
                    publish_date = position['createTime'].split(' ')[0]
                    # 判断是否是当天发布
                    if not handle.compare_datetime(publish_date):
                        self.logger.info('已不是当天：%s' % position['createTime'])
                        return False
                    url = self.job_url % position['positionId']
                    if url in self.urls or self.lagou_db.isexist_url(url):
                        self.logger.debug('此url %s 已经存在！' % url)
                        continue
                    self.urls.append(url)
                    item['url'] = url
                    item['publish_date'] = publish_date
                    item['position_name'] = position['positionName'].strip()
                    item['work_year'] = position['workYear'].strip()
                    item['education'] = position['education'].strip()
                    item['job_nature'] = position['jobNature'].strip()
                    item['salary'] = position['salary'].strip()
                    item['city'] = position['city'].strip()
                    item['district'] = position['district'].strip() if position['district'] else ''
                    item['company_name'] = position['companyShortName'].strip()
                    item['job_detail'] = ''
                    item['job_address'] = ''
                    g = gevent.spawn(self.get_position_detail, url, item, cookies=cookies)
                    self.pool.add(g)
                    # self.get_position_detail(url, item, cookies=cookies)

        return True

    # 获取详情页的数据
    def get_position_detail(self, url, position, cookies=None):
        position = copy.deepcopy(position)
        response = request.get(url=url, cookies=cookies)
        self.request_count += 1
        if response:
            html = etree.HTML(response.content)
            self.logger.info(html.xpath('//title/text()')[0] if html.xpath('//title/text()') else 'title error ')
            job_detail = html.xpath("//dd[@class='job_bt']/div//text()")
            job_detail = [item.strip() for item in job_detail if item.strip()]
            job_detail = '\n'.join(job_detail).strip()

            job_address = html.xpath("//div[@class='work_addr']//text()")
            job_address = [item.strip() for item in job_address]
            job_address = ''.join(job_address[:-2])

            position['job_detail'] = job_detail
            position['job_address'] = job_address
        else:
            self.except_count += 1
        self.save_infos(position)

    # 过滤url和时间
    def filter_url(self, position_data, url):
        """
         过滤url和时间
        :param position_data:
        :param url:
        :return:
        """
        if not handle.compare_datetime(position_data) or \
                self.lagou_db.isexist_url(url) or \
                url in self.urls:
            return False
        else:
            self.urls.append(url)
            return True


if __name__ == '__main__':
    # for i in range(20):
    #     save_infos().next()

    # print(filter_url('2018-1-4','https://www.lagou.com/jobs/356274.html'))
    start_time = time.time()
    t = RealTime()
    t.start_spider()
    print(t.count)
    end_time = time.time()
    run_time = end_time - start_time
    print('运行: %s seconds' % (run_time))


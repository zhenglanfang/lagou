#! /usr/bin/python
# coding=utf-8

import sys

sys.path.append('/Users/mrs/Desktop/project/mytest/lagou/lagou_spider')

import time
import random

from lxml import etree
from database import db_operate
from util import request
from util import handle
from spider.base import LagouBase

form_data = {
    'first':'false',
    'pn':'3',
    'kd':'ios',
}


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
        response = request.get(url, cookies=cookies)
        cookies = response.cookies
        self.get_new_list(response, item, cookies)

    # 获取最新的职位列表
    def get_new_list(self, response, item, cookies):
        if response:
            # new_url = html.xpath("//div[@class='item order']/a[2]/@href")
            new_url = self.second_url % (item['first_type'])
            response = request.get(url=new_url, cookies=cookies)
            if response:
                referer = response.url
                html = etree.HTML(response.content)
                page_num = html.xpath("//span[@class='span totalNum']/text()")
                page_num = int(page_num[0]) if page_num else 1
                for num in range(1, page_num + 1):
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
                        try:
                            result = response.json(encoding='utf-8')
                        except Exception as e:
                            print(e.message)
                        else:
                            if result.get('success'):
                                result = self.get_positions_urls(result, item, cookies=response.cookies)
                                if not result:
                                    return
                                break
                            else:
                                print('%s %s %s' % (self.post_url, form_data, response.text))

    # 获取列表页的urls
    def get_positions_urls(self, result, item, cookies):
        content = result.get('content')
        if content:
            if content.get('positionResult'):
                positions = content.get('positionResult').get('result')
                for position in positions:
                    publish_date = position['createTime'].split(' ')[0]
                    # 判断是否是当天发布
                    if not handle.compare_datetime(publish_date):
                        print('已不是当天：%s' % position['createTime'])
                        return False
                    url = self.job_url % position['positionId']
                    if db_operate.isexist_url(url):
                        print('此url %s 已经存在！' % url)
                        continue
                    item['url'] = url
                    item['publish_date'] = publish_date
                    item['position_name'] = position['positionName']
                    item['work_year'] = position['workYear']
                    item['education'] = position['education'].strip()
                    item['job_nature'] = position['jobNature']
                    item['salary'] = position['salary']
                    item['city'] = position['city']
                    item['district'] = position['district'] if position['district'] else ''
                    item['company_name'] = position['companyShortName']
                    item['job_detail'] = ''
                    item['job_address'] = ''
                    response = request.get(url=url, cookies=cookies)
                    self.get_position_detail(response, item)

        return True

    # 获取详情页的数据
    def get_position_detail(self, response, position):
        if response:
            html = etree.HTML(response.content)
            print(html.xpath('//title/text()')[0] if html.xpath('//title/text()') else 'title error ')
            job_detail = html.xpath("//dd[@class='job_bt']/div//text()")
            job_detail = [item.strip() for item in job_detail if item.strip()]
            job_detail = '\n'.join(job_detail).strip()

            job_address = html.xpath("//div[@class='work_addr']//text()")
            job_address = [item.strip() for item in job_address]
            job_address = ''.join(job_address[:-2])

            position['job_detail'] = job_detail
            position['job_address'] = job_address

        self.save_infos(position)

    # 过滤url和时间
    @staticmethod
    def filter_url(position_data, url):
        """
         过滤url和时间
        :param position_data:
        :param url:
        :return:
        """
        if not handle.compare_datetime(position_data) or db_operate.isexist_url(url):
            return False
        else:
            return True


if __name__ == '__main__':
    # for i in range(20):
    #     save_infos().next()

    # print(filter_url('2018-1-4','https://www.lagou.com/jobs/356274.html'))
    RealTime().start_spider()

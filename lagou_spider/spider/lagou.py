#! /usr/bin/python
# coding=utf-8

import sys
sys.path.append('/Users/mrs/Desktop/project/mytest/lagou/lagou_spider')

import datetime
from lxml import etree
from database import db_operate
from util import request
from spider.base import LagouBase

start_url = 'https://www.lagou.com/'
second_url = 'https://www.lagou.com/jobs/list_%s?px=default&city=全国#order'


class AllLagou(LagouBase):
    '''
        定期整站爬取
    '''

    def __init__(self):
        super(AllLagou, self).__init__()

    # 获取职位列表页
    def get_positons_list(self, url, item, cookies):
        response = request.get(url, cookies=cookies)
        cookies = response.cookies
        if response:
            html = etree.HTML(response.content)
            title = html.xpath('//title/text()')
            if not title or title[0] == '找工作-互联网招聘求职网-拉勾网':
                print(url + '  error ')
                return
            self.get_positions_urls(response, item, cookies)
            html = etree.HTML(response.content)
            page_num = html.xpath("//span[@class='span totalNum']/text()")
            page_num = int(page_num[0]) if page_num else 1
            if page_num > 1:
                for num in range(2, page_num + 1):
                    list_url = '%s%d/' % (url, num)
                    response = request.get(list_url, cookies=cookies)
                    self.get_positions_urls(response, item, response.cookies)

    # 获取列表页的urls
    def get_positions_urls(self, response, item, cookies):
        if response:
            html = etree.HTML(response.content)
            print(html.xpath('//title/text()')[0] if html.xpath('//title/text()') else 'title error')
            item_list = html.xpath("//ul[@class='item_con_list']/li")
            for position in item_list:
                publish_date = position.xpath(".//span[@class='format-time']/text()")[0]
                publish_date = self.switch_publish_date(publish_date)
                url = position.xpath(".//a[@class='position_link']/@href")[0]
                # 判断url是否存在
                if not db_operate.isexist_url(url):
                    position_name = position.xpath("@data-positionname")[0]
                    salary = position.xpath("@data-salary")[0]
                    other = position.xpath(".//div[@class='li_b_l']/text()")[2].strip()
                    add = position.xpath(".//span[@class='add']/em/text()")[0]
                    city = add.split('·')[0]
                    company_name = position.xpath("@data-company")[0]
                    item['position_name'] = position_name
                    item['publish_date'] = publish_date
                    item['salary'] = salary
                    item['education'] = other.split('/')[1]
                    item['work_year'] = other.split('/')[0][2:]
                    item['city'] = city
                    item['company_name'] = company_name
                    item['url'] = url
                    response = request.get(url, cookies=cookies)
                    self.get_position_detail(response, item)
                else:
                    print('此url %s 已经存在！' % url)

    # 获取详情页的数据
    def get_position_detail(self, response, position):
        if response:
            html = etree.HTML(response.content)
            print(html.xpath('//title/text()')[0] if html.xpath('//title/text()') else 'title error ')
            # education = html.xpath("//dd[@class='job_request']/p[1]/span[4]/text()")
            # work_year = html.xpath("//dd[@class='job_request']/p[1]/span[3]/text()")
            job_nature = html.xpath("//dd[@class='job_request']/p[1]/span[5]/text()")
            # education = str(education[0]).strip('/') if education else ''
            # work_year = str(work_year[0]).strip('/') if work_year else ''
            job_nature = job_nature[0] if job_nature else ''
            job_detail = html.xpath("//dd[@class='job_bt']/div//text()")
            job_detail = [item.strip() for item in job_detail if item.strip()]
            job_detail = '\n'.join(job_detail).strip()
            job_address = html.xpath("//div[@class='work_addr']//text()")
            job_address = [item.strip() for item in job_address]
            job_address = ''.join(job_address[:-2])
            district = html.xpath("//div[@class='work_addr']/a[2]/text()")
            district = district[0] if district else ''
            position['job_nature'] = job_nature
            position['job_detail'] = job_detail
            position['job_address'] = job_address
            position['district'] = district
        self.save_infos(position)

    # 转换时间
    @staticmethod
    def switch_publish_date(publish_date):
        '''
        处理发布时间
        :param publish_date:
        :return:
        '''
        if publish_date.endswith('发布'):
            today = datetime.date.today()
            if publish_date.find(':') == -1:
                delta = int(publish_date[0])
                publish_date = today - datetime.timedelta(days=delta)
                return publish_date
            else:
                return today
        else:
            return publish_date


if __name__ == '__main__':
    # for i in range(20):
    #     save_infos().next()
    import time
    start_time = time.time()
    AllLagou().start_spider()
    end_time = time.time()
    run_time = end_time - start_time
    print('运行: %s seconds' % (run_time))
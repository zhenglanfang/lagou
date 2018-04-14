#! /usr/bin/python
# coding=utf-8


import sys
import os
dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(dir_path)))

from lxml import etree

from lagou_spider.database import dbmysql
from lagou_spider.util import request
from lagou_spider.util.handle import print_log


def update_data():
    db = dbmysql.DB()
    sql = "select * from positions where publish_date > '2018-04-06'"
    #sql = "select * from (select * from positions limit 1,100) " \
    #      "as t where t.publish_date > '2018-03-16'"
    positions = db.fetchall(sql)
    for position in positions:
        try:
            city, district = position['job_address'].split('-')[0:2]
        except Exception as e:
            city = ''
            district = ''
        if city == position['city'] and district == position['district']:
            pass
        else:
            response = request.get(position['url'])
            html = etree.HTML(response.content)
            # education = html.xpath("//dd[@class='job_request']/p[1]/span[4]/text()")
            # work_year = html.xpath("//dd[@class='job_request']/p[1]/span[3]/text()")
            # job_nature = html.xpath("//dd[@class='job_request']/p[1]/span[5]/text()")
            # education = str(education[0]).strip('/') if education else ''
            # work_year = str(work_year[0]).strip('/') if work_year else ''
            # job_nature = job_nature[0].strip() if job_nature else ''
            job_detail = html.xpath("//dd[@class='job_bt']/div//text()")
            job_detail = [item.strip() for item in job_detail if item.strip()]
            job_detail = '\n'.join(job_detail).strip()
            job_address = html.xpath("//div[@class='work_addr']//text()")
            job_address = [item.strip() for item in job_address]
            job_address = ''.join(job_address[:-2])
            # district = html.xpath("//div[@class='work_addr']/a[2]/text()")
            # district = district[0].strip() if district else ''
            # position['job_nature'] = job_nature
            # position['job_detail'] = job_detail
            # position['job_address'] = job_address
            position = dict(position)
            position['publish_date'] = str(position['publish_date'])
            print_log(position['url'],position)
            sql = 'update positions set job_address=:job_address,job_detail=:job_detail where url=:url'
            db.edit(sql,{'job_detail':job_detail,'job_address':job_address,'url':position['url']})


if __name__ == '__main__':
    update_data()

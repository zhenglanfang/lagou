#! /usr/bin/python
# coding=utf-8
import sys
import os
dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(dir_path)))

from lagou_spider import config
from lagou_spider.util import log
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text



# 配置文件中读取连接串
# DB_URI = config.DB.MYSQL_PROD
# pool_size连接池数量
# pool_recycle连接池中空闲时间超过设定时间后，进行释放
# echo输出日志
# create_engine 初始化数据库连接

class DB(object):
    """数据库基类"""
    def __init__(self):
        self.engine = create_engine(
            config.MYSQL_PROD, echo=False,pool_size=50, pool_recycle=1800)
        self.logger = log.logger

    # 插入，修改，删除操作
    def edit(self, sql, params=None):
        """
        作用：插入，修改，删除 数据
        :param sql: 执行sql
        :param params: 查询参数
        :return: 受影响的行数
        """
        # 创建DBSession类型:
        DB_Session = sessionmaker(bind=self.engine)
        # 创建session对象:
        db = DB_Session()
        try:
            # 执行sql语句
            result = db.execute(text(sql), params)
            db.commit()
            return result.rowcount
        except Exception as ex:
            self.logger.error("exec sql got error:%s" % (ex))
            db.rollback()
            return False
        finally:
            db.close()
    
    # 查询第一条数据
    def first(self, sql, params=None):
        """
        作用：查询第一条数据
        :param sql: 查询语句
        :param params: 查询参数
        :return: 查询数据
        first():返回元组，如果没有查询到数据返回None
        """
        # 创建DBSession类型:
        DB_Session = sessionmaker(bind=self.engine)
        # 创建session对象:
        db = DB_Session()
        try:
            # 执行sql语句，.first  session对象返回第一条数据
            #
            rs = db.execute(text(sql),params).first()
            db.commit()
            return rs
        except Exception as ex:
            self.logger.error("exec sql got error:%s" % ex)
            db.rollback()
            return False
        finally:
            db.close()
    
    # 查询多条数据
    def fetchall(self, sql, params=None):
        """
        作用：查询多条数据
        :param sql: 查询语句
        :param params: 查询参数
        :return: 查询数据
        fetchall(): 返回列表，里面是元组；如果没有查询到返回 []
        """
        # 创建DBSession类型:
        DB_Session = sessionmaker(bind=self.engine)
        # 创建session对象:
        db = DB_Session()
        try:
            # 执行sql语句,.fetchall  session对象返回全部数据
            rs = db.execute(text(sql),params).fetchall()
            db.commit()
            return rs
        except Exception as ex:
            self.logger.error("exec sql got error:%s" % ex)
            db.rollback()
            return False
        finally:
            db.close()

def test():
    db = DB()
    # :url  代表参数
    # sql = 'insert into urls(url,insert_time) values(:url,:insert_time)'
    from datetime import datetime
    # rs = db.edit(sql,{'url':'py2','insert_time':datetime.now()})
    # print(rs)
    sql = 'select * from urls where url=:url'
    rs = db.fetchall(sql,{'url':'py'})
    # 结果：[(2, u'py'), (4, u'py'), (5, u'py')]
    rs = db.fetchall(sql, {'url': 'p'})
    # 结果：[]
    rs = db.first(sql,{'url':'中国'})
    # 结果：(6, u'中国')
    rs = db.first(sql, {'url': '中'})
    # 结果：None
    print(rs)

if __name__ == '__main__':
    test()

#! /usr/bin/python
# coding=utf-8
import sys
import os
dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(dir_path)))

import pandas as pd
import numpy as np

from lagou_spider.database import dbmysql

db = dbmysql.DB()

sql = 'select * from positions'
result = db.fetchall(sql)
columns = result[0]._parent.keys
df = pd.DataFrame(result, columns=columns)
df['year'] = pd.to_datetime(df['publish_date']).dt.year

def positions_rank():
    result = {}
    grouped = df.groupby('year')
    for name, group in grouped:
        first_type_counts = group['first_type'].value_counts()
        counts = first_type_counts.sum()
        score = first_type_counts.head(10) / counts
        print(group['first_type'].value_counts().head(10))


def position_type_distribute():
    pass


def city_position_distribute():
    pass

if __name__ == '__main__':
    positions_rank()



#!/usr/bin/python
# -*- coding: UTF-8 -*-
import pymysql
from peewee import *

from lib.config import Config

DBinfo = Config.DBConfig

db = MySQLDatabase(
    DBinfo.MYSQL_DANAME,
    user='root',
    password='123456',
    host='localhost',
    port=DBinfo.MYSQL_PORT,
    charset='utf8mb4'
)
my_conn = pymysql.connect(
    user='root',
    password='123456',
    host='localhost',
    port=DBinfo.MYSQL_PORT,
    charset='utf8mb4',
    db=DBinfo.MYSQL_DANAME,
)


class BaseModel(Model):
    class Meta:
        database = db


class WechatInfo(BaseModel):
    url = CharField(null=True)
    jobTypeId = CharField(null=True)  # data_job_type 关联
    title = CharField(null=True)
    content = TextField(null=True)  # 数据库中改为 longtext
    desc = TextField(null=True)  # 描述
    createAt = DateTimeField(null=True)  # 创建时间
    updateAt = DateTimeField(null=True)  # 更新时间
    commentCount = IntegerField(default=0)  # 评论数
    voteCount = IntegerField(default=0)  # 投票/喜欢数
    readCount = IntegerField(default=0)  # 阅读数
    wechatName = CharField(null=True)  # 公众号名称
    wechatId = CharField(null=True)  # 公众号id
    biz = CharField(null=True)

    class Meta:
        table_name = 'data_wechat_job_info'


class UnableProxies(BaseModel):
    object = CharField(null=True, unique=True)
    good_or_bad = CharField(default='bad')


class CrawledData(BaseModel):
    main_url = CharField()
    target = CharField


class SaveDate(BaseModel):
    biz = CharField()
    title = CharField()
    error = CharField()
    object = CharField(unique=True)
    page = IntegerField()

    class Meta:
        table_name = 'saved_data'


if __name__ == '__main__':
    db.create_tables([WechatInfo,
                      UnableProxies,
                      CrawledData,
                      SaveDate,
                      ])

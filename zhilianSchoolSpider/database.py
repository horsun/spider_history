#!/usr/bin/python
# -*- coding: UTF-8 -*-

from peewee import *

from lib.config import Config

DBinfo = Config.DBConfig

db = MySQLDatabase(DBinfo.MYSQL_DANAME,
                   user=DBinfo.MYSQL_USER,
                   password='123456',
                   host=DBinfo.MYSQL_HOST,
                   port=int(DBinfo.MYSQL_PORT))


class BaseModel(Model):
    class Meta:
        database = db


class Major(BaseModel):
    name = TextField()
    url = TextField()
    pages = TextField()


class MajorDetail(BaseModel):
    major_id = ForeignKeyField(Major)
    jobName = TextField()  # title
    companyName = TextField()  # 公司名称
    url = TextField()  # 详细url
    description = TextField()
    cityName = TextField()  # 所在城市
    companyIndustry = TextField()  # 所属行业v
    jobType = TextField()  # 工作类型  v
    hireNumber = TextField()  # 招聘人数 v
    postTime = TextField()  # 发布时间 v


class Ratio(BaseModel):
    cityName = CharField(max_length=100)
    jobType = CharField(max_length=100)
    count = IntegerField()

    class meta:
        table_name = 'data_ratio'


if __name__ == '__main__':
    db.connect()
    db.create_tables([Major,
                      MajorDetail,
                      Ratio,
                      ])

#!/usr/bin/python
# -*- coding: UTF-8 -*-

from peewee import *

from lib.config import Config

DBinfo = Config.DBConfig

db = MySQLDatabase(DBinfo.MYSQL_DANAME,
                   user=DBinfo.MYSQL_USER,
                   password=str(DBinfo.MYSQL_PASSWD),
                   host=DBinfo.MYSQL_HOST,
                   port=DBinfo.MYSQL_PORT)


class BaseModel(Model):
    class Meta:
        database = db


class MajorGenerality(BaseModel):
    name = TextField()
    parent_id = ForeignKeyField('self', null=True)
    major_id = TextField(null=True)
    sort = TextField(null=True)
    job_recommend = TextField(null=True)
    level = TextField()


class MajorDetail(BaseModel):
    generality_id = ForeignKeyField(MajorGenerality)
    introduction = TextField(null=True)
    trainTarget = TextField(null=True)
    mainMajor = TextField(null=True)
    knowledgePower = TextField(null=True)
    jobTarget = TextField(null=True)
    jobZoom = TextField(null=True)
    jobList = TextField(null=True)


if __name__ == '__main__':
    db.connect()
    db.create_tables([MajorGenerality,
                      MajorDetail,
                      ])

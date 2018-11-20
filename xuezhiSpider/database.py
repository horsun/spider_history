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


class Occupation(BaseModel):
    name = TextField()
    url_id = CharField(null=True, unique=True, max_length=255)
    kt_id = CharField(null=True, unique=True, max_length=255)
    xl_id = TextField(null=True)
    parent_id = ForeignKeyField('self',
                                null=True)
    level = TextField()
    detail = TextField(null=True)


class Major(BaseModel):
    major_name = CharField(max_length=255)
    star_value = TextField()  # 综合满意度 （3.5 、 4.5）
    edu_level = TextField()  # 学历层次（本科、专科）
    kind = TextField()  # 门类（哲学、 经济学）
    course = TextField()  # 学科（哲学类、经济学类）
    detail = TextField()
    url = CharField(null=True, unique=True, max_length=255)


if __name__ == '__main__':
    db.connect()
    db.create_tables([Major, Occupation])

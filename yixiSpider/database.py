#!/usr/bin/python
# -*- coding: UTF-8 -*-

from peewee import *

from lib.config import Config

DBinfo = Config.DBConfig

db = MySQLDatabase(
    DBinfo.MYSQL_DANAME,
    user=DBinfo.MYSQL_USER,
    password=str(DBinfo.MYSQL_PASSWD),
    host=DBinfo.MYSQL_HOST,
    port=DBinfo.MYSQL_PORT,
    charset='utf8mb4'
)


class BaseModel(Model):
    class Meta:
        database = db


class YiXiInfo(BaseModel):
    unique_id = CharField(verbose_name='唯一标识id', max_length=8)  # id
    title = CharField(null=True)  # title
    tags = CharField(null=True)  # speechcategory
    post_time = DateTimeField(null=True, verbose_name='发布时间')  # created
    talker = CharField(null=True, verbose_name='讲师')  # speaker['name']
    talker_intro = CharField(null=True, verbose_name='讲师介绍')  # speaker['intro']
    speech_article = TextField(null=True, verbose_name='演讲词')  # titlelanguage
    main_pic_url = CharField(null=True, verbose_name='封面url')  # titlelanguage
    video_url = CharField(null=True, verbose_name='视频地址')  # video[0]['video_url']

    class Meta:
        table_name = 'data_yixi_speech'


if __name__ == '__main__':
    db.create_tables([YiXiInfo])

# -*- coding: UTF-8 -*-


from lib.config import Config
from peewee import *

DBinfo = Config.DBConfig

db = MySQLDatabase(
    DBinfo.MYSQL_DANAME,
    user=DBinfo.MYSQL_USER,
    password=str(DBinfo.MYSQL_PASSWD),
    host=DBinfo.MYSQL_HOST,
    port=DBinfo.MYSQL_PORT,
    charset='utf8mb4'
)


# id(自增序列就好了), url, title, desc, content, createAt, updateAt, commentCount, voteCount, readCount，type, json(前面说的整个JSON字符串)
# ID，URL，标题，描述，内容，创建时间，更新时间，评论数，投票数／喜欢数，阅读数(如果有的话)，类型(top_answers/search_result)，原始数据


class BaseModel(Model):
    class Meta:
        database = db


class ZhiHuInfo(BaseModel):
    url = CharField(null=True)
    jobTypeId = CharField(null=True)  # data_job_type 关联
    title = CharField(null=True)
    content = TextField(null=True)
    desc = TextField(null=True)  # 描述
    createAt = DateTimeField(null=True)  # 创建时间
    updateAt = DateTimeField(null=True)  # 更新时间
    commentCount = IntegerField(default=0)  # 评论数
    voteCount = IntegerField(default=0)  # 投票/喜欢数
    readCount = IntegerField(default=0)  # 阅读数
    type = CharField(null=True)
    json = TextField(null=True)

    class Meta:
        table_name = 'data_zhihu_job_info'


class SavedData(BaseModel):
    url_path = CharField(max_length=100, unique=True, null=True)
    page = IntegerField(default=0)

    class Meta:
        table_name = "data_saved"


if __name__ == '__main__':
    db.create_tables([ZhiHuInfo,
                      SavedData])

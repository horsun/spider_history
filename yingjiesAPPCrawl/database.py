from peewee import *

from lib.config import Config

DBinfo = Config.DBConfig

db = MySQLDatabase(
    DBinfo.MYSQL_DANAME,
    user=DBinfo.MYSQL_USER,
    password=str(DBinfo.MYSQL_PASSWD),
    host=DBinfo.MYSQL_HOST,
    port=DBinfo.MYSQL_PORT,
    charset='utf8mb4',
)


class BaseModel(Model):
    class Meta:
        database = db


class CompanyList(BaseModel):
    cid = IntegerField(unique=True)
    cname = CharField(max_length=30, null=True)
    industryname = CharField(max_length=100, null=True)

    class Meta:
        table_name = 'data_company_list'


class CompanyDetail(BaseModel):
    cid = IntegerField()
    linkid = IntegerField()
    content = TextField()
    linktype = CharField(max_length=50)
    linkurl = CharField(max_length=200)
    addtime = IntegerField()
    add_date_time = DateTimeField()

    class Meta:
        table_name = 'data_company_detail'


class ZzJobInfo(BaseModel):
    jobid = IntegerField(unique=True)
    title = CharField(max_length=200)
    detail = TextField()

    class Meta:
        table_name = 'data_company_zzjobinfo'


class BbsThreadInfo(BaseModel):
    threadid = IntegerField(unique=True)
    title = CharField(max_length=200)
    detail = TextField()

    class Meta:
        table_name = 'data_company_bbsthreadinfo'


class MixData(BaseModel):
    cid = IntegerField()
    cname = CharField(max_length=30)
    industryname = CharField(max_length=100)
    linktype = CharField(max_length=50)
    title = CharField(max_length=200)
    url = TextField()
    addtime = DateTimeField()

    class Meta:
        table_name = "data_mix_data"


if __name__ == '__main__':
    db.create_tables(
        [
            CompanyList,
            CompanyDetail,
            ZzJobInfo,
            BbsThreadInfo,
            MixData,
        ]
    )

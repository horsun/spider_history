# -*- coding: UTF-8 -*-


from lib.config import Config
from peewee import *

DBinfo = Config.DBConfig

db = MySQLDatabase(
    DBinfo.MYSQL_DANAME,
    user=DBinfo.MYSQL_USER,
    password=str(DBinfo.MYSQL_PASSWD),
    host=DBinfo.MYSQL_HOST,
    port=DBinfo.MYSQL_PORT)


class BaseModel(Model):
    class Meta:
        database = db


class jobType(BaseModel):
    name = TextField()
    parent_id = ForeignKeyField("self", null=True)
    level = IntegerField()
    code = CharField(null=True)


class jobDetail(BaseModel):
    jobName = TextField(null=True)
    detailUrl = CharField(null=True, max_length=64)
    typeCode = CharField(null=True)
    areaCode = CharField(null=True)
    monthMoney = TextField(null=True)
    workAddress = TextField(null=True)
    companyName = TextField(null=True)
    education = TextField(null=True)
    detailContent = TextField(null=True)
    companySize = TextField(null=True)
    companyKind = TextField(null=True)
    jobYears = TextField(null=True)
    companyUrl = TextField(null=True)


class monthMoneyAvg(BaseModel):
    jobTypeId = IntegerField()
    avgSalary = DoubleField()
    avgSalaryMin = DoubleField()
    avgSalaryMax = DoubleField()
    source = IntegerField()

    class Meta:
        table_name = 'data_job_type_salary'


if __name__ == '__main__':
    db.create_tables([jobType,
                      jobDetail,
                      monthMoneyAvg, ])

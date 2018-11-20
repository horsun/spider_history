from peewee import *
from lib.config import Config

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


class TalkInfo(BaseModel):
    title = TextField(null=True)
    speaker = TextField(null=True)
    url = CharField(null=True, unique=True, )
    post_time = TextField(null=True)
    speaker_info = TextField(null=True)
    main_pic = TextField(null=True)


class TalkDetail(BaseModel):
    video_url = TextField(null=True)
    content = TextField(null=True)
    talkinfo_id = ForeignKeyField(TalkInfo, unique=True)


if __name__ == "__main__":
    db.connect()
    db.create_tables([TalkInfo, TalkDetail])

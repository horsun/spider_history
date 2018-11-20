from peewee import *
from lib.config import Config

DBinfo = Config.DBConfig

db = MySQLDatabase(
    DBinfo.MYSQL_DANAME,
    user=DBinfo.MYSQL_USER,
    password=str(DBinfo.MYSQL_PASSWD),
    host=DBinfo.MYSQL_HOST,
    port=DBinfo.MYSQL_PORT,
    charset='utf8mb4')


class BaseModel(Model):
    class Meta:
        database = db


class SpeechList(BaseModel):
    unique_talk_id = CharField(max_length=8)
    title_en = CharField(max_length=100)
    title_zh = TextField()
    detail_url = CharField(unique=True)
    pic_url = TextField()
    post_date = TextField()
    author = TextField()
    author_info_en = TextField()
    author_info_zh = TextField()
    speech_intro_en = TextField()
    speech_intro_zh = TextField()
    full_speech = TextField(null=True)
    full_speech_en = TextField(null=True)
    category = TextField()
    identity = TextField()


if __name__ == "__main__":
    db.connect()
    db.create_tables([SpeechList])

import re
import pymysql
from database import *

file = open('./basedata.js', 'r', encoding='utf8').read()


def get_area_map():
    code_string_re = 'dDistrict =([\s\S]*)'
    result = re.findall(code_string_re, file)
    name_re = '@(.*?)\|(.*?)\|'
    code_list = re.findall(name_re, result[0])
    print(code_list)
    areaMap = {}
    for item in code_list:
        code, name = item
        areaMap[code] = name

    return areaMap


def getConn():
    conn = pymysql.connect(
        host=DBinfo.MYSQL_HOST,
        port=DBinfo.MYSQL_PORT,
        user=DBinfo.MYSQL_USER,
        passwd=str(DBinfo.MYSQL_PASSWD),
        db=DBinfo.MYSQL_DANAME,
        charset='utf8')
    return conn


def get_area_require_count():
    conn = getConn()
    cursor = conn.cursor()
    sdl = """ SELECT DISTINCT(detailUrl),COUNT(*) as count,areaCode from jobdetail GROUP BY areaCode ORDER BY count DESC"""


if __name__ == '__main__':
    get_area_map()
    all ()

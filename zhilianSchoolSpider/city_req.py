from pprint import pprint

import pymysql
from database import *
from database import *


# @property
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
    my_cursor = getConn().cursor()
    while True:
        sql = """SELECT COUNT(*) as count,cityName,jobType from  majordetail GROUP BY jobType,cityName ORDER BY count DESC """
        my_cursor.execute(sql)
        data = my_cursor.fetchall()
        for item in data:
            Ratio.create(
                cityName=item[1],
                jobType=item[2],
                count=item[0],

            )
            print(item, 'saved')
    my_cursor.close()
    getConn().close()


if __name__ == '__main__':
    get_area_require_count()

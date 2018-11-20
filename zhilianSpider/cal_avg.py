# -*- coding: UTF-8 -*-
import logging

from database import *
import pymysql

avg_table = monthMoneyAvg()

DBinfo = Config.DBConfig


class ResultCalc(object):
    def __init__(self):
        self.logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s [%(threadName)s][%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    def getConn(self):
        conn = pymysql.connect(
            host=DBinfo.MYSQL_HOST,
            port=DBinfo.MYSQL_PORT,
            user=DBinfo.MYSQL_USER,
            passwd=str(DBinfo.MYSQL_PASSWD),
            db=DBinfo.MYSQL_DANAME,
            charset='utf8')
        return conn

    def avg_cal(self):
        """
        对data_job_type_salary 进行计算
        :return:
        """
        conn = self.getConn()
        cursor = conn.cursor()
        cursor.execute("""SELECT code FROM jobtype  where level = '3'""")
        data = cursor._rows
        for item in data:
            code = item[0]
            avg_min_sql = """SELECT typeCode, AVG(substring_index(monthMoney,'-',1)) from jobdetail where typeCode ='{0}' and monthMoney!='面议';""".format(
                code)
            avg_max_sql = """SELECT typeCode, AVG(substring_index(monthMoney,'-',-1)) from jobdetail where typeCode ='{0}' and monthMoney!='面议';""".format(
                code)
            cursor.execute(avg_min_sql)
            avg_min = round(cursor._rows[0][1], 2)
            cursor.execute(avg_max_sql)
            avg_max = round(cursor._rows[0][1], 2)
            avg_table.create(
                jobTypeId=int(code),
                avgSalary=round((avg_min + avg_max) / 2, 2),
                avgSalaryMin=avg_min,
                avgSalaryMax=avg_max,
                source=2,
            )

    def industry_avg_cal(self):
        """
        对 data_industry进行 avg
        :return:
        """
        conn = self.getConn()
        cursor = conn.cursor()
        for i in range(19):
            # update level = 1 main industry
            sql = """SELECT AVG(avgSalary) from data_job_type_salary where jobTypeId in (
                      SELECT DISTINCT jobTypeId from data_industry_jobtype where industryId in (
                      SELECT industryId from data_industry where `level` = '2' and source = 'zhilian' and parentId = {0}))""".format(
                i + 1)
            cursor.execute(sql)
            data = cursor._rows
            sql = """ update data_industry  set avgSalary = {0} where  industryId = {1}""".format(round(data[0][0], 2),
                                                                                                  i + 1)
            cursor.execute(sql)
            conn.commit()

        sql = """SELECT industryId from data_industry WHERE `level` = '2' and source = 'zhilian'"""
        cursor.execute(sql)
        data = cursor.fetchall()
        for industryId, in data:
            # update level = 2 second industry
            sql = """SELECT AVG(avgSalary) as avgSalary  from data_job_type_salary WHERE jobTypeId in(SELECT jobTypeId from data_industry_jobtype where industryId  = {0})""".format(
                industryId)
            cursor.execute(sql)
            data = cursor.fetchall()
            sql = """ update data_industry  set avgSalary = {0} where  industryId = {1}""".format(round(data[0][0], 2),
                                                                                                  industryId)
            cursor.execute(sql)
            conn.commit()


if __name__ == '__main__':
    cal_avg_table = ResultCalc()
    cal_avg_table.avg_cal()  # data_job_type_salary  ---->>>> avg min_avg max_avg
    # cal_avg_table.industry_avg_cal()    # data_industry         ---->>>> avgSalary

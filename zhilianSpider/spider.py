# -*- coding: UTF-8 -*-


import datetime
import logging
import re
import time
# from datetime import datetime
from pprint import pprint

import pymysql
import requests
from database import *
from queue import Queue
from threading import Thread

# from BloomCheck import *
# from redis_bloom import *

job_type = jobType()
job_detail = jobDetail()

file = open('./basedata.js', 'r', encoding='utf8').read()


def get_area_map():
    code_string_re = 'dDistrict =([\s\S]*)'
    result = re.findall(code_string_re, file)
    name_re = '@(.*?)\|(.*?)\|'
    code_list = re.findall(name_re, result[0])
    areaMap = {}
    for item in code_list:
        code, name = item
        areaMap[code] = name

    return areaMap


areaMap = get_area_map()


def get_base_jobType():
    jobtypeClass = [{'id': '20', 'name': '销售|客服|市场'}, {'id': '21', 'name': '财务|人力资源|行政'},
                    {'id': '22', 'name': '项目|质量|高级管理'}, {'id': '23', 'name': 'IT|互联网|通信'},
                    {'id': '24', 'name': '房产|建筑|物业管理'}, {'id': '25', 'name': '金融'}, {'id': '26', 'name': '采购|贸易|交通|物流'},
                    {'id': '27', 'name': '生产|制造'}, {'id': '28', 'name': '传媒|印刷|艺术|设计'},
                    {'id': '29', 'name': '咨询|法律|教育|翻译'},
                    {'id': '30', 'name': '服务业'}, {'id': '31', 'name': '能源|环保|农业|科研'},
                    {'id': '32', 'name': '兼职|实习|社工|其他'}]
    main_data = open('./first_data.txt')
    info = main_data.read().split('\n')
    info.remove('')
    # for item in info:
    #     job_type.create(
    #         name=item,
    #         level=1,
    #         code=None,
    #     )
    for item in jobtypeClass:
        job_type.create(
            name=item['name'],
            level=1,
            code=item['id'],
        )
    second_type_re = "dJobtype='(.*?)'"
    result = re.findall(second_type_re, file)
    result = result[0].split('@')
    result = [x for x in result if x.strip()]
    # pprint(result)
    for item in result:
        item = item.split('|')
        job_type.create(
            name=item[1],
            code=item[0],
            level=2,
            parent_id=None
        )
    third_type_re = "dSubjobtype = '(.*?)'"
    result = re.findall(third_type_re, file)
    result = result[0].split('@')
    result = [x for x in result if x.strip()]
    pprint(result)
    for item in result:
        item = item.split('|')
        print(item)
        job_type.create(
            name=item[1],
            code=item[0],
            level=3,
            parent_id=job_type.get(code=item[2]).id
        )


class SpiderCrawl(object):
    def __init__(self):
        self.logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s [%(threadName)s][%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
        SpiderConfig = Config.SpiderConfig
        self.headers = SpiderConfig.headers.json()
        self.init()

    def getConn(self):
        conn = pymysql.connect(
            host=DBinfo.MYSQL_HOST,
            port=DBinfo.MYSQL_PORT,
            user=DBinfo.MYSQL_USER,
            passwd=str(DBinfo.MYSQL_PASSWD),
            db=DBinfo.MYSQL_DANAME,
            charset='utf8')
        return conn

    def init(self):
        # print(datetime.datetime.now())
        sql = """select detailUrl from jobdetail"""
        conn = self.getConn()
        cursor = conn.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        self.urlList = [item for item, in data]
        self.urlSet = set(self.urlList)

    def get_info(self, areaCode, count):
        for item in job_type.select().where(jobType.level == 3):
            typeCode = item.code
            url = 'https://sou.zhaopin.com/jobs/searchresult.ashx?&isadv=0&sj={0}&re={1}'.format(typeCode, areaCode)
            while True:
                try:
                    html = requests.get(url=url,
                                        headers=self.headers,
                                        timeout=5).text
                    break
                except Exception as e:
                    print('5 seconds continue')

            zwyx = '<td class="zwyx">(.*?)</td>'  # 职位月薪
            zwyx = re.findall(zwyx, html)
            gzdd = '<td class="gzdd">(.*?)</td>'  # 工作地点
            gzdd = re.findall(gzdd, html)
            gsmc = '<td class="gsmc"><a href="(.*?)" target="_blank">(.*?)</a>'  # 公司url +公司名称
            gsmc = re.findall(gsmc, html)
            zwmc = '<a style="font-weight: bold" par="(.*?)" href="(.*?)" target="_blank">(.*?)</a>'  # par + 详细url+ 职位名称
            zwmc = re.findall(zwmc, html)
            gsxz = '公司性质：(.*?)</span>'
            gsxz = re.findall(gsxz, html)
            xlyq = '学历：(.*?)</span>'
            xlyq = re.findall(xlyq, html)
            detail = '<li class="newlist_deatil_last">(.*?)</li></li>'
            detail = re.findall(detail, html)
            gsgm = '公司规模：(.*?)</span>'
            gsgm = re.findall(gsgm, html)
            gzjy = '<li class="newlist_deatil_two"><span>(.*?)</span><li class="newlist_deatil_last">'
            gzjy = re.findall(gzjy, html)
            get_year_Re = '经验：(.*?)</span>'
            conditions = '共<em>(.*?)</em>个职位满足条件'
            conditions = re.findall(conditions, html)
            conditions = int(conditions[0])
            print(conditions)
            if conditions > 60:
                conditions = 60
            for num in range(conditions):
                try:
                    job_year_req = re.findall(get_year_Re, gzjy[num])
                except:
                    print(url, num)
                companyUrl = gsmc[num][0] if gsmc[num:num + 1] else []
                jobYears = ''.join(job_year_req) if job_year_req.__len__() != 0 else '不限'
                detailUrl = zwmc[num][1] if zwmc[num][1:2] else []
                typeCode = typeCode
                areaCode = areaCode
                target_url = zwmc[num][1]
                if target_url not in self.urlSet:
                    try:
                        job_detail.create(
                            jobName=zwmc[num][2] if zwmc[num][2:3] else [],
                            detailUrl=zwmc[num][1] if zwmc[num][1:2] else [],
                            typeCode=typeCode,
                            areaCode=areaCode,
                            monthMoney=zwyx[num] if zwyx[num:num + 1] else [],
                            workAddress=gzdd[num] if gzdd[num:num + 1] else [],
                            companyName=gsmc[num][1] if gsmc[num:num + 1] else [],
                            education=xlyq[num] if xlyq[num:num + 1] else [],
                            detailContent=detail[num] if detail[num:num + 1] else [],
                            companySize=gsgm[num] if gsgm[num:num + 1] else [],
                            companyKind=gsxz[num] if gsxz[num:num + 1] else [],
                            companyUrl=gsmc[num][0] if gsmc[num:num + 1] else [],
                            jobYears=jobYears
                        )
                    except Exception as e:
                        data = {
                            'jobName': zwmc[num][2] if zwmc[num][2:3] else [],
                            'detailUrl ': zwmc[num][1] if zwmc[num][1:2] else [],
                            'typeCode ': typeCode,
                            'areaCode ': areaCode,
                            'monthMoney ': zwyx[num] if zwyx[num:num + 1] else [],
                            'workAddress ': gzdd[num] if gzdd[num:num + 1] else [],
                            'error_num': num,
                        }
                        self.logger.warning(str(data))
                else:
                    print('pass for exist')
                    pass
                    # job_detail.update(jobYears=jobYears,
                    #                   companyUrl=companyUrl).where(
                    #     jobDetail.detailUrl == detailUrl).execute()


if __name__ == '__main__':
    # get_base_jobType()  # 第一次运行先解禁这条
    spider = SpiderCrawl()
    target = []
    q = Queue()
    Thread_num = 10
    for item in areaMap.keys():
        q.put(item)


    def run():
        index = 0
        while True:
            item = q.get()
            spider.get_info(item, index)
            q.task_done()
            index += 1


    for i in range(Thread_num):
        t = Thread(target=run)
        t.setDaemon(True)
        t.start()
    q.join()

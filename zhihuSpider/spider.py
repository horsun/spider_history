import logging
import time
from pprint import pprint

import pymysql

from database import *
import requests
import json


class Crawl(object):
    def __init__(self):
        self.logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s [%(threadName)s][%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
        SpiderConfig = Config.SpiderConfig
        self.headers = SpiderConfig.headers.json()
        self.get_conn()
        self.targetUrl = 'https://www.zhihu.com/api/v4/search_v3?t=general&q={0}&correction=1&offset=0&limit=200&search_hash_id=9adf82c9cb360361901f871c64315846'
        self.get_finished_type_id_list()
        self.zh_db = ZhiHuInfo()
        self.count = 0
        self.error_list = []

    def get_finished_type_id_list(self):
        sql = """select DISTINCT (jobTypeId) from data_zhihu_job_info """
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        self.finished_type_id_list = []
        for jobTypeId, in data:
            self.finished_type_id_list.append(jobTypeId)
        # return finished_type_id_list

    def get_conn(self):
        conn = pymysql.connect(
            host=DBinfo.MYSQL_HOST,
            port=DBinfo.MYSQL_PORT,
            user=DBinfo.MYSQL_USER,
            passwd=str(DBinfo.MYSQL_PASSWD),
            db=DBinfo.MYSQL_DANAME,
            charset='utf8')
        return conn

    def create_target(self):
        target_list = []
        conn = self.get_conn()
        cursor = conn.cursor()
        sql = """select jobTypeId , jobTypeName from data_job_type where level = '3'"""
        cursor.execute(sql)
        data = cursor.fetchall()
        print(data.__len__())
        for num, item in enumerate(data):
            jobTypeId = item[0]
            jobTypeName = item[1]
            target = {
                'jobTypeId': jobTypeId,
                'jobTypeName': jobTypeName,
                'targetUrl': self.targetUrl.format(jobTypeName)
            }
            target_list.append(target)
        cursor.close()
        return target_list

    def get_data(self, target):
        count = 0
        error = []
        targetUrl = target['targetUrl']
        targetTypeId = target['jobTypeId']
        if self.check_data(target):
            print('data exist')
        else:
            html = requests.get(url=targetUrl, headers=self.headers, )
            html.encoding = 'utf-8'
            html = html.text
            s = json.loads(html)
            for item in s['data']:
                if item['type'] == 'search_result':
                    count += 1
                    try:
                        self.zh_db.create(
                            url=item['object']['url'] if 'url' in item['object'].keys() else None,
                            jobTypeId=targetTypeId,
                            title=item['highlight']['title'] if 'title' in item['highlight'].keys() else None,
                            content=item['object']['content'].strip() if 'content' in item['object'].keys() else None,
                            desc=item['highlight']['description'] if 'description' in item[
                                'highlight'].keys() else None,
                            createAt=time.strftime('%Y-%m-%dT%H:%M:%S',
                                                   time.localtime(item['object']['created_time'])) if 'created_time' in
                                                                                                      item[
                                                                                                          'object'].keys() else None,
                            updateAt=time.strftime('%Y-%m-%dT%H:%M:%S',
                                                   time.localtime(item['object']['updated_time'])) if 'updated_time' in
                                                                                                      item[
                                                                                                          'object'].keys() else None,
                            commentCount=item['object']['comment_count'] if 'comment_count' in item[
                                'object'].keys() else 0,
                            voteCount=item['object']['voteup_count'] if 'voteup_count' in item['object'].keys() else 0,
                            # readCount=item['object']['voteup_count'],
                            type='top_answers',
                            json=str(item).strip()
                        )
                    except Exception as e:
                        pprint(item)
                        error.append(str(item).strip() + '\n' + '_warning : ' + e.__repr__() + '\n')
                        self.logger.warning(str(e.__repr__()))
                        time.sleep(8888)
                else:
                    print('pass one drop')
            if count == 0:
                self.count += 1
                print(self.count)
                self.error_list.append(target)
                pprint(self.error_list)
                # 不存在的情况下 进行别的操作
                jobTypeName = target['jobTypeName']
                jobTypeName = jobTypeName.split('/')
                for item in jobTypeName:
                    url = 'https://www.zhihu.com/api/v4/search_v3?t=topic&q={0}&correction=1&offset=0&limit=200'.format(
                        item)
                    html = requests.get(url=url, headers=self.headers, )
                    html.encoding = 'utf-8'
                    html = html.text
                    s = json.loads(html)
                    print('length:__ ' + str(s['data'].__len__()))
                    for item in s['data']:
                        if item['type'] == 'search_result':
                            count += 1
                            try:
                                self.zh_db.create(
                                    url=item['object']['url'] if 'url' in item['object'].keys() else None,
                                    jobTypeId=targetTypeId,
                                    title=item['highlight']['title'] if 'title' in item['highlight'].keys() else None,
                                    content=item['object']['content'].strip() if 'content' in item[
                                        'object'].keys() else None,
                                    desc=item['highlight']['description'] if 'description' in item[
                                        'highlight'].keys() else None,
                                    createAt=time.strftime('%Y-%m-%dT%H:%M:%S',
                                                           time.localtime(
                                                               item['object']['created_time'])) if 'created_time' in
                                                                                                   item[
                                                                                                       'object'].keys() else None,
                                    updateAt=time.strftime('%Y-%m-%dT%H:%M:%S',
                                                           time.localtime(
                                                               item['object']['updated_time'])) if 'updated_time' in
                                                                                                   item[
                                                                                                       'object'].keys() else None,
                                    commentCount=item['object']['comment_count'] if 'comment_count' in item[
                                        'object'].keys() else 0,
                                    voteCount=item['object']['voteup_count'] if 'voteup_count' in item[
                                        'object'].keys() else 0,
                                    # readCount=item['object']['voteup_count'],
                                    type='search_result',
                                    json=str(item).strip()
                                )
                            except Exception as e:
                                pprint(item)
                                error.append(str(item).strip() + '\n' + '_warning : ' + e.__repr__() + '\n')
                                self.logger.warning(str(e.__repr__()))
                                time.sleep(8888)
                        else:
                            print('pass one drop')

                pprint(target)

            pprint(error)
            # time.sleep(2)

    def check_data(self, target):
        targetTypeId = target['jobTypeId']
        if targetTypeId in self.finished_type_id_list:
            return True
        else:
            return False


if __name__ == '__main__':
    spider = Crawl()
    target_list = spider.create_target()
    for target in target_list:
        spider.get_data(target)

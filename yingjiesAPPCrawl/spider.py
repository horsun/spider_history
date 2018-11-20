import json
import logging
import threading
import time
from queue import Queue

import pymysql
import requests

from database import *


class Crawl():
    def __init__(self):
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('peewee').setLevel(logging.WARNING)
        self.logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s [%(threadName)s][%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
        self.company_list = CompanyList()
        self.company_detail = CompanyDetail()
        self.zzjobinfo = ZzJobInfo()
        self.bbsthreadinfo = BbsThreadInfo()
        self.mix_table = MixData()

    def get_company(self):
        url = 'https://app.yingjiesheng.com/app/?module=famous&sessid=&userid=&page=1&pernum=3000'
        html = requests.get(url=url)
        html.encoding = 'utf-8'
        html = json.loads(html.text)
        result = html['resultbody']['items']
        company_list = []
        for item in result:
            company_list.append({
                'cid': item['cid'],
                'cname': item['cname'],
                'industryname': item['industryname']
            })
            try:
                self.company_list.create(
                    cid=item['cid'],
                    cname=item['cname'],
                    industryname=item['industryname'],

                )
            except IntegrityError:
                self.logger.debug('in process %s %s has saved' % ('company_list', item['cname']))

        return company_list, result

    def get_conn(self):
        conn = pymysql.connect(
            host=DBinfo.MYSQL_HOST,
            port=DBinfo.MYSQL_PORT,
            user=DBinfo.MYSQL_USER,
            passwd=str(DBinfo.MYSQL_PASSWD),
            db=DBinfo.MYSQL_DANAME,
            charset='utf8')
        return conn

    def save_data(self, company, item):
        """
        公用数据保存方法
        :param company:
        :return:
        """
        error = []
        cdetail = {}
        try:
            cdetail.clear()
            date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(item['addtime'])))
            self.company_detail.create(
                cid=company['cid'],
                linkid=item['linkid'],
                content=item['content'],
                linktype=item['linktype'],
                linkurl=item['linkurl'],
                addtime=item['addtime'],
                add_date_time=date_time,
            )
        except Exception as e:
            self.logger.debug(
                'in process %s company %s error : %s' % ('company_detail', item['content'], e.__repr__()))
            return
        cdetail['linktype'] = item['linktype']
        if item['linktype'] == 'bbsthreadid':
            request_url = 'https://bbsapp.yingjiesheng.com/51jobyjs.php?act=get_view_thread&tid={0}'.format(
                item['linkid'])
            while True:
                try:
                    detail_html = requests.get(url=request_url)
                    detail_html.encoding = 'utf-8'
                    break
                except ConnectionError:
                    self.logger.debug('request error :timeout ')
            try:
                detail_json = json.loads(detail_html.text, strict=False)
            except Exception as e:
                self.logger.debug(
                    ' in process json loads request url : %s  error %s' % (request_url, e.__repr__()))
                return
            if detail_json['result'] != '400':
                cdetail['linkUrl'] = 'http://bbs.yingjiesheng.com/forum.php?mod=viewthread&tid={0}'.format(
                    detail_json['tid'])
                cdetail['content'] = detail_json['title']
                try:
                    self.bbsthreadinfo.create(
                        threadid=detail_json['tid'],
                        title=detail_json['title'],
                        detail=str(detail_json),
                    )
                except IntegrityError:
                    self.logger.debug(
                        'in process %s %s has saved' % ('bbsthreadinfo', detail_json['tid']))

                except InternalError:
                    error.append(cdetail['linkUrl'])
                    print(cdetail['linkUrl'])
            else:
                return
        elif cdetail['linktype'] == 'zzjobid':
            request_url = 'https://app.yingjiesheng.com/app/?module=zzjobview&jobid={0}'.format(
                item['linkid'])
            while True:
                try:
                    detail_html = requests.get(url=request_url)
                    detail_html.encoding = 'utf-8'
                    break
                except ConnectionError:
                    self.logger.debug('request error :timeout ')
            try:
                detail_json = json.loads(detail_html.text, strict=False)
            except Exception as e:
                self.logger.debug(
                    ' in process json loads request url : %s  error %s' % (request_url, e.__repr__()))
                return
            if detail_json['result'] != '400':
                cdetail['linkUrl'] = detail_json['resultbody']['fromurl']
                cdetail['content'] = detail_json['resultbody']['title']
                try:
                    self.zzjobinfo.create(
                        jobid=detail_json['resultbody']['jobid'],
                        title=detail_json['resultbody']['title'],
                        detail=str(detail_json),
                    )
                except IntegrityError:
                    self.logger.debug(
                        'in process %s %s has saved' % ('zzjobinfo', detail_json['resultbody']['jobid']))

                except InternalError:
                    error.append(cdetail['linkUrl'])
                    print(cdetail['linkUrl'])
            else:
                return
        elif cdetail['linktype'] == 'pcurl':
            cdetail['linkUrl'] = item['linkurl']
            cdetail['content'] = item['content']
        else:
            return
        try:
            self.mix_table.create(
                cid=company['cid'],
                cname=company['cname'],
                industryname=company['industryname'],
                linktype=cdetail['linktype'],
                title=cdetail['content'],
                url=cdetail['linkUrl'],
                addtime=date_time,
            )
        except IntegrityError:
            self.logger.debug('in process %s %s has saved' % ('mix_table', cdetail['content']))

    def get_company_detail(self):
        company_list, origin_company_data = self.get_company()

        for company in company_list:
            view_url = 'https://app.yingjiesheng.com/app/?module=famousview&cid={0}'
            url = view_url.format(company['cid'])
            html = requests.get(url)
            html.encoding = 'utf-8'
            html = json.loads(html.text)
            for item in html['resultbody']['items']:
                self.save_data(company, item)


class UpdateCheck(Crawl):
    def __init__(self):
        super(UpdateCheck).__init__()
        self.get_ord_data()

    def get_cid_list(self):
        company_list_query = self.company_list.select()
        company_list = []
        for company in company_list_query:
            company_list.append(company.cid)
        return company_list

    def get_ord_data(self):
        company_detail_query = self.company_detail.select()
        self.company_detail_list = []
        for company_detail in company_detail_query:
            self.company_detail_list.append((company_detail.content, str(company_detail.addtime)))

    def check_update(self, target_cid):
        company_detail = self.company_list.get(CompanyList.cid == target_cid)
        company_url = 'https://app.yingjiesheng.com/app/?module=famousview&cid={0}'.format(target_cid)
        html = requests.get(url=company_url)
        html.encoding = 'utf-8'
        data_json = json.loads(html.text)
        company = {}
        for detail in data_json['resultbody']['items']:
            company.clear()
            if (detail['content'], str(detail['addtime'])) in self.company_detail_list:
                self.logger.debug('pass %s item  for exist ' % (detail['content']))
                continue
            else:
                self.logger.debug('detail:%s is new,now in process save data' % detail['content'])
                company['cid'] = company_detail.cid
                company['cname'] = company_detail.cname
                company['industryname'] = company_detail.industryname
                self.save_data(company, detail)


if __name__ == '__main__':

    update = UpdateCheck()
    # update.get_company_detail()#获取全部数据
    # 下面 获取更新数据
    q = Queue()
    thread_num = 10
    for cid in update.get_cid_list():
        q.put(cid)


    def run():
        while True:
            target_cid = q.get()
            update.check_update(target_cid)
            q.task_done()


    for i in range(thread_num):
        t = threading.Thread(target=run)
        t.setDaemon(True)
        t.start()
    q.join()

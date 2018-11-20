#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging
import random
import re
import time
from pprint import pprint
from queue import Queue
from threading import Thread

try:
    from urllib import parse
except Exception as e:
    from urllib import quote
import pymysql
import requests
import wechatsogou
from wechatsogou.structuring import WechatSogouStructuring
import traceback
from database import *
from rk import RClient
from lib.proxy import NewGenerationProxy


class Crawl(object):
    def __init__(self):
        logging.getLogger("wechatsogou").setLevel(logging.WARNING)
        logging.getLogger("peewee").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        self.logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s [%(threadName)s][%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
        self.get_bad_proxies()
        self.WxTable = WechatInfo()
        self.get_conn()
        self.create_target()
        self.get_saved_data()
        self.proxies_list = NewGenerationProxy({'anony': 'L4', 'post': 'false', 'speed': 3000})
        proxyLine = self.proxies_list.getProxy()
        self.wx_api = wechatsogou.WechatSogouAPI(timeout=8, proxies={'http': proxyLine, 'https': proxyLine})
        SpiderConfig = Config.SpiderConfig
        self.headers = SpiderConfig.headers.json()
        self.weChat_table = WechatInfo()
        self.proxies_table = UnableProxies()
        self.crawled_table = CrawledData()
        self.rk = RClient('ghost2017b', 'Ghost2017b', '107539', 'a8bd936aa1574ddb96d14564c1a0d022')

    def get_conn(self):
        conn = pymysql.connect(
            host=DBinfo.MYSQL_HOST,
            port=DBinfo.MYSQL_PORT,
            user=DBinfo.MYSQL_USER,
            passwd=str(DBinfo.MYSQL_PASSWD),
            db=DBinfo.MYSQL_DANAME,
            charset='utf8')
        return conn

    def get_saved_data(self):
        conn = self.get_conn()
        cursor = conn.cursor()
        sql = """select main_url from crawleddata"""
        cursor.execute(sql)
        self.saved_data_list = [x for x, in cursor.fetchall()]

    def get_bad_proxies(self):
        conn = self.get_conn()
        cursor = conn.cursor()
        sql = """select object from unableproxies """
        cursor.execute(sql)
        self.bad_proxies_list = [x for x, in cursor.fetchall()]

    def create_target(self):
        self.target_list = []
        conn = self.get_conn()
        cursor = conn.cursor()
        sql = """select jobTypeId , jobTypeName from data_job_type where level = '3'"""
        cursor.execute(sql)
        data = cursor.fetchall()
        for num, item in enumerate(data):
            jobTypeId = item[0]
            jobTypeName = item[1]
            target = {
                'jobTypeId': jobTypeId,
                'jobTypeName': jobTypeName,
                'items': []
            }
            self.target_list.append(target)
        cursor.close()

    # def get_proxy(self, scene='default'):
    #     while True:
    #         # url = 'http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=c6ffc08035cc49f49ed15c834ba2c8ee&orderno=YZ20185305368PAYAqN&returnType=1&count=1'
    #         # url = 'http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=c6ffc08035cc49f49ed15c834ba2c8ee&orderno=YZ2018634506zLQTDj&returnType=2&count=1'
    #         # url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
    #         url = 'http://dev.kdlapi.com/api/getproxy/?orderid=953059683695998&num=1&b_pcchrome=1&b_pcie=1&b_pcff=1&protocol=2&method=1&an_an=1&an_ha=1&sep=1'
    #         html = requests.get(url).text
    #         time.sleep(random.randint(5, 10))
    #         if re.findall('普通订单5秒钟内只允许提取1次', html):
    #             self.logger.debug('need to get proxy ' + scene + ' again!')
    #             continue
    #
    #         try:
    #             proxyLine = html
    #             proxies = {
    #                 'https': proxyLine
    #             }
    #         except:
    #             pprint(html)
    #             continue
    #
    #         if str(proxies) in self.bad_proxies_list:
    #             self.logger.debug('ip is bad')
    #             continue
    #         else:
    #             self.logger.debug(u'Update %s proxy to %s' % (scene, proxyLine))
    #             return proxies  # proxyLine   proxies

    '''
        for run.py
    '''

    def get_target_list(self, target):
        page = 10
        keyword = target['jobTypeName']
        target['items'] = []
        target['main_url'] = []
        for i in range(page):
            url = u'http://weixin.sogou.com/weixin?type=2&page=%s&ie=utf8&query=%s&interation=' % (
                i + 1, parse.quote(str(keyword)))
            if url in self.saved_data_list:
                self.logger.debug('the url had been crawled %s/%s' % (keyword, i + 1))
                continue
            while True:
                def identify_image_callback(image):
                    result = self.rk.rk_create(image, 3060)
                    if 'Result' in result:
                        self.logger.debug(u'Captcha: %s, ID: %s' % (result['Result'], result['Id']))
                        return result['Result']
                    self.logger.debug(result)
                    return ''

                try:
                    target_little_list = self.wx_api.search_article(
                        target['jobTypeName'], page=i + 1,
                        identify_image_callback=identify_image_callback,
                    )
                    target['main_url'].append(url)
                    self.logger.debug(
                        u'Name: %s, Page: %s, Count: %s' % (target['jobTypeName'], i, len(target_little_list)))
                    break
                except Exception as e:
                    self.logger.debug(traceback.format_exc())
                    self.logger.debug(u'Name: %s, Page: %s, Error: %s' % (target['jobTypeName'], i, e.__repr__()))
                    proxyLine = self.proxies_list.getProxy()
                    self.logger.debug(u'Update proxy to %s' % (proxyLine))
                    self.wx_api.requests_kwargs['proxies'] = {
                        "https": proxyLine,
                    }
            if target_little_list.__len__() == 0:
                break
            target['items'].append(target_little_list)
        return target

    def get_target_list_v2(self, target):
        page = 10
        keyword = target['jobTypeName']
        target['items'] = []
        target['main_url'] = []
        first_data = 'init_proxy'
        for i in range(page):
            while True:
                url = u'http://weixin.sogou.com/weixin?type=2&page=%s&ie=utf8&query=%s&interation=' % (
                    i + 1, parse.quote(keyword))
                self.headers['Referer'] = url
                self.headers['Cookie'] = 'SUV="";SNUID="";'
                if url not in self.saved_data_list:
                    try:
                        self.logger.debug("queue get before size:%s" % q_proxies.qsize())
                        proxies = q_proxies.get()
                        self.logger.debug("queue get after size :%s" % q_proxies.qsize())
                        resp = requests.get(url,
                                            proxies=proxies,
                                            headers=self.headers,
                                            timeout=8,
                                            )
                        if resp.ok:
                            if u'antispider' in resp.url:
                                # TODO:记录一下被识别为爬虫的代理IP到数据库 #
                                self.proxies_table.create(
                                    object=proxies['http'],
                                )
                                self.logger.debug(
                                    u'Name: %s, Page: %s, DetachAntiSpider: %s' % (
                                        keyword, str(i + 1), proxies['http']))
                                first_data = 'detach_spider'
                                continue
                            else:
                                time.sleep(random.randint(2, 5))
                                target_little_list = WechatSogouStructuring.get_article_by_search(resp.text)
                                if target_little_list.__len__() == 0:
                                    break  # break for the page doesnt have data
                                target['items'].append(target_little_list)
                                target['main_url'].append(url)
                                self.logger.debug(
                                    'get item %s page %d total %d ' % (keyword, i + 1, target_little_list.__len__()))
                                break  # break for success
                        else:
                            self.logger.debug(
                                u'Name: %s, Page: %s, HttpError: %s' % (keyword, str(i + 1), str(resp.status_code)))
                            first_data = 'http_error'
                    except Exception as e:
                        self.logger.debug(u'Name: %s, Page: %s, Error: %s' % (keyword, i + 1, type(e)))
                        first_data = 'catch_exception'
                else:
                    self.logger.debug('the url had been crawled')
                    break  # break for exist
        self.logger.debug(u'Name: %s, Total: %s' % (keyword, len(target['items'])))
        return target

    def get_data(self, target):
        try:
            for num, topItem in enumerate(target['items']):
                url = target['main_url'][num]
                self.crawled_table.create(
                    main_url=url,
                    target=target['jobTypeName'],
                )
                for item in topItem:
                    detail_url = item['article']['url']
                    html = requests.get(url=detail_url,
                                        headers=self.headers
                                        ).text
                    content = re.findall('<div class="rich_media_content " lang=="en" id="js_content">([\s\S]*)</div>',
                                         html)
                    biz = re.findall('var biz = ""\|\|"(.*?)"', html)
                    is_delete = re.findall('该内容已被发布者删除', html)
                    if is_delete.__len__() == 0:
                        wechatId = re.findall('"profile_meta_value">(.*?)</span>', html)
                        if wechatId.__len__() == 0:
                            wechatId = ''
                        elif wechatId[0] == '':
                            wechatId = ''
                        else:
                            wechatId = wechatId[0]
                        if biz.__len__() == 0:
                            biz = ''
                        else:
                            biz = biz[0]
                        obj_wechat = self.weChat_table.create(
                            url=detail_url,
                            jobTypeId=target['jobTypeId'],
                            title=item['article']['title'],
                            content=''.join(content),
                            desc=item['article']['abstract'],
                            createAt=time.strftime('%Y-%m-%dT%H:%M:%S',
                                                   time.localtime(item['article']['time'])),
                            wechatId=wechatId,
                            wechatName=item['gzh']['wechat_name'],
                            biz=biz,
                        )
                        self.logger.debug('item: %s save id: %s' % (target['jobTypeName'], str(obj_wechat.id)))
                    else:
                        self.logger.debug('pass for item is deleted by author')
        except Exception as e:
            self.logger.warning('something wrong : ' + e.__repr__())


def test(inProxy=None):
    api = wechatsogou.WechatSogouAPI(timeout=8)
    proxyLine = '54.223.188.100:6666'
    proxyLine = '140.227.80.50:3128'  # antispider
    proxyLine = '114.110.21.146:53281'
    proxyLine = '45.6.216.79:80'
    proxyLine = '133.18.55.242:80'  # antispider
    proxyLine = '85.114.25.202:8080'  # OK
    proxyLine = '159.89.163.248:53281'  # antispider
    proxyLine = '110.164.181.164:8080'
    proxyLine = '200.87.134.30:53281'
    proxyLine = '115.203.219.81:33885'  # OK
    proxyLine = '180.122.147.226:24636'  # antispider
    if inProxy != None:
        proxyLine = inProxy

    if proxyLine != None:
        api.requests_kwargs['proxies'] = inProxy
    print(proxyLine)
    result = api.search_article('Java')
    pprint(result)


def get_proxy(scene='default'):
    """
    代理加入队列
    :param scene:
    :return:
    """
    while True:
        url = 'http://dev.kdlapi.com/api/getproxy/?orderid=973068503334549&num=50&b_pcchrome=1&b_pcie=1&b_pcff=1&protocol=2&method=1&an_an=1&an_ha=1&sep=1'
        html = requests.get(url).text
        time.sleep(5)
        if re.findall('普通订单5秒钟内只允许提取1次', html):
            crawl.logger.debug('need to get proxy ' + scene + ' again!')
            continue
        try:
            ip_list = html.split('\r\n')
            return ip_list
        except:
            pprint(html)
            continue


if __name__ == '__main__':
    crawl = Crawl()
    count = 0
    total = crawl.target_list.__len__()

    q_proxies = Queue()


    def main(target):
        first_target = crawl.get_target_list_v2(target)
        crawl.get_data(first_target)


    q = Queue()
    Thread_num = 10
    for item in crawl.target_list:
        q.put(item)


    def run():
        while True:
            item = q.get()
            crawl.logger.debug(str(total - q.qsize()) + '/' + str(total))
            main(item)
            q.task_done()


    def run2(q_proxies):
        while True:
            if q_proxies.qsize() < Thread_num * 3:
                ip_list = get_proxy()
                for item in ip_list:
                    q_proxies.put({
                        "http": item
                    })
                print('get')

            # q_proxies.task_done()


    for i in range(Thread_num):
        if i == 0:
            t1 = Thread(target=run2, kwargs={'q_proxies': q_proxies})
            t1.setDaemon(True)
            t1.start()
        else:
            t = Thread(target=run)
            t.setDaemon(True)
            t.start()
    q.join()

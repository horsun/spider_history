import re
from queue import Queue
from threading import Thread

import pymysql
from lxml import html as lxml_html

from database import *
from google_translate import *
from lib.proxy import *


class TedSpider(object):
    def __init__(self):
        logging.getLogger('peewee').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        self.logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s [%(threadName)s][%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
        SpiderConfig = Config.SpiderConfig
        self.headers = SpiderConfig.headers.json()
        self.SpeechList = SpeechList()
        self.gg_trans = GGTranslate()
        self.proxy = ScyllaProxy()
        self.get_crawled_url()

    def getConn(self):
        conn = pymysql.connect(
            host=DBinfo.MYSQL_HOST,
            port=DBinfo.MYSQL_PORT,
            user=DBinfo.MYSQL_USER,
            passwd=str(DBinfo.MYSQL_PASSWD),
            db=DBinfo.MYSQL_DANAME,
            charset='utf8')
        return conn

    def getProxy(self):
        proxy = NewGenerationProxy().getProxy()
        print(proxy)
        return {'http': proxy}

    def get_crawled_url(self):
        all_url_list = self.SpeechList.select(SpeechList.detail_url)
        self.url_list = [x.detail_url for x in all_url_list]

    def get_ted_list(self, page):
        main_url = 'https://www.ted.com/talks?page=' + str(page)
        while True:
            try:
                html = requests.get(url=main_url,
                                    headers=self.headers,
                                    timeout=10,
                                    proxies=self.getProxy(),
                                    verify=False,
                                    ).text
                break
            except:
                pass
        doc = lxml_html.fromstring(html)
        title = '//*[@id="browse-results"]/div[1]/div/div/div/div/div[2]/h4[2]/a/text()'
        url = '//*[@id="browse-results"]/div[1]/div/div/div/div/div[2]/h4[2]/a/@href'
        date = '//*[@id="browse-results"]/div[1]/div/div/div/div/div[2]/div/span[1]/span/text()'
        pic = '//*[@id="browse-results"]/div[1]/div/div/div/div/div[1]/a/span/span[1]/span/img/@src'
        author = '//*[@id="browse-results"]/div[1]/div/div/div/div/div[2]/h4[1]/text()'
        title = doc.xpath(title)  # 中英文
        url = doc.xpath(url)
        date = doc.xpath(date)
        pic = doc.xpath(pic)  # split("?")
        author = doc.xpath(author)
        for num, target in enumerate(title):
            detail_url = 'https://www.ted.com' + url[num]
            if detail_url not in self.url_list:
                while True:
                    try:
                        html = requests.get(url=detail_url,
                                            headers=self.headers,
                                            verify=False,
                                            # timeout=5,
                                            proxies=self.getProxy(),
                                            ).text
                        bad = re.findall('429 Rate Limited too many requests', html)
                        if bad.__len__() != 0:
                            self.logger.debug('spider has been found need rest')
                            self.logger.debug('request time out ,rest 5 sec')
                            # time.sleep(5)
                            continue
                        break
                    except:
                        time.sleep(5)
                        self.logger.debug('request main html time out ,rest 5 sec')
                string = re.findall('"__INITIAL_DATA__":([\s\S]*)</script></div>', html)

                try:
                    detail = string[0]
                    full_json = json.loads(detail[:-2])
                    url = 'https://www.ted.com/talks/{0}/transcript.json?language=zh-cn'.format(
                        full_json['comments']['talk_id'])
                    url_en = 'https://www.ted.com/talks/{0}/transcript.json'.format(full_json['comments']['talk_id'])
                    while True:
                        try:
                            html = requests.get(url=url,
                                                headers=self.headers,
                                                verify=False,
                                                # timeout=5,
                                                # proxies=self.getProxy(),
                                                ).text
                            print(url)
                            full_speech = ''
                            if re.findall('Not Found', html).__len__() == 0:
                                zh_json = json.loads(html)
                                for item in zh_json['paragraphs']:
                                    for item_2 in item['cues']:
                                        full_speech += item_2['text']
                            else:
                                return
                            break
                        except:
                            self.logger.debug('request translate zh time out ,rest 5 sec')
                    while True:
                        try:
                            html_en = requests.get(url=url_en,
                                                   headers=self.headers,
                                                   verify=False,
                                                   # timeout=5,
                                                   # proxies=self.getProxy(),

                                                   ).text
                            print(url_en)
                            full_speech_en = ''
                            if re.findall('Not Found', html_en).__len__() == 0:
                                zh_json = json.loads(html_en)
                                for item in zh_json['paragraphs']:
                                    for item_2 in item['cues']:
                                        full_speech_en += item_2['text']
                            else:
                                return
                            break
                        except:
                            self.logger.debug('request translate en time out ,rest 5 sec')
                    self.SpeechList.create(
                        title_en=target,
                        title_zh=target,  # self.gg_rans.translate(item),
                        detail_url=detail_url,
                        pic_url=''.join(pic[num]).split('?')[0],
                        post_date=date[num],
                        author=author[num],
                        unique_talk_id=full_json['comments']['talk_id'],
                        author_info_en=full_json['speakers'][0]['whotheyare'] if full_json[
                                                                                     'speakers'].__len__() != 0 else 'None',
                        author_info_zh=full_json['speakers'][0]['whotheyare'] if full_json[
                                                                                     'speakers'].__len__() != 0 else "None",
                        speech_intro_en=full_json['description'],
                        speech_intro_zh=full_json['description'],
                        category=full_json['talks'][0]['tags'],
                        identity=full_json['speakers'][0]['description'] if full_json[
                                                                                'speakers'].__len__() != 0 else "None",
                        full_speech=full_speech,
                        full_speech_en=full_speech_en,
                    )
                except IndexError as e:
                    self.logger.debug(string)
                    self.logger.debug(full_json['comments']['talk_id'])
                    self.logger.debug(type(e))
                    self.logger.debug(detail_url)
                    self.logger.debug(e.__repr__())
                except IntegrityError:
                    self.logger.debug('speech is exsits for same url')
            else:
                self.logger.debug('url: %s has been saved' % detail_url)

    def translate_title_author(self, unique_talk_id):
        sl = self.SpeechList
        target = sl.get(SpeechList.unique_talk_id == unique_talk_id)
        target.title_zh = self.gg_trans.translate(target.title_zh)
        target.author_info_zh = self.gg_trans.translate(target.author_info_zh)
        target.speech_intro_zh = self.gg_trans.translate(target.speech_intro_zh)
        if target.full_speech == target.full_speech_en:
            target.full_speech = self.gg_trans.translate(target.full_speech_en)
        target.save()


def muti_process(item_count, ):
    thread_num = 3
    q = Queue()
    if isinstance(item_count, int):
        for i in range(int(item_count)):
            q.put(i + 1)

        def run():
            while True:
                item = q.get()
                ted_spider.get_ted_list(item)
                q.task_done()
    else:
        for item in item_count:
            q.put(item)

        def run():
            while True:
                item = q.get()
                ted_spider.translate_title_author(item)  # 翻译标题等
                q.task_done()

    for i in range(thread_num):
        t = Thread(target=run)
        t.setDaemon(True)
        t.start()
    q.join()


if __name__ == '__main__':
    ted_spider = TedSpider()
    print(ted_spider.headers)
    while True:
        try:
            html = requests.get(url='https://www.ted.com/talks',
                                verify=False,
                                headers=ted_spider.headers,
                                timeout=5,
                                ).text
            break
        except Exception as e:
            ted_spider.logger.debug(e.__repr__())

    doc = lxml_html.fromstring(html)
    pages = '//*[@id="browse-results"]/div[2]/div/a[5]/text()'
    target = int(''.join(doc.xpath(pages)).strip())  # 爬内容
    muti_process(target)
    conn = ted_spider.getConn()
    cursor = conn.cursor()
    sql = """select unique_talk_id from speechlist where title_en=title_zh"""  # 翻译标题 及 简介
    cursor.execute(sql)
    conn.close()
    target = [x for x, in cursor.fetchall()]  # 爬翻译
    muti_process(target)

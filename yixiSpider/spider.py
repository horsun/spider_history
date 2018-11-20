import json
import logging
import requests
from datetime import datetime
from database import *

headers = {
    'content-type': 'application/json',
    'Host': 'api2.yixi.tv',
    'User-Agent': 'okhttp/3.5.0',
    'appVersion': '3.0.6',
    'deviceOs': 'Android',
}


class Crawl(object):
    def __init__(self):
        self.url = 'https://api2.yixi.tv/api/v1/speech/all/?speech_category_id=&order_by=-speechdate&page=1&pageSize=720'  # 全部文章
        logging.getLogger("peewee").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        self.logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s [%(threadName)s][%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
        self.yixi_table = YiXiInfo
        self.get_api_json()

    def get_api_json(self):
        html = requests.get(url=self.url)
        self.html_json = json.loads(html.text)
        self.logger.debug("target length :%s" % (self.html_json['data']['speech_total']))

    def save_data(self):
        for item in self.html_json['data']['speechs']:
            self.yixi_table.create(
                unique_id=item['speech_id'],
                title=item['title'],
                tags=item['speechcategory'],
                post_time=datetime.strptime(item['created'].replace('.', '-'), '%Y-%m-%d'),
                talker=item['speaker']['name'],
                talker_intro=item['speaker']['intro'],
                speech_article=item['titlelanguage'],
                main_pic_url=item['video_cover'],
                video_url=item['video'][0]['video_url']

            )
            self.logger.debug('save speech_id %s ' % item['speech_id'])

    def update(self):
        url = 'https://api2.yixi.tv/api/v1/speech/?speech_id={0}'
        for item in self.yixi_table.select():
            unique_id = item.unique_id
            main_url = url.format(unique_id)
            html = requests.get(url=main_url).text
            j_son = json.loads(html)
            article = j_son['data']['speech']['draft']
            update_obj = self.yixi_table.get(unique_id=unique_id)
            update_obj.speech_article = article
            update_obj.save()
            print(update_obj.speech_article)
            print(1)


if __name__ == '__main__':
    crawl = Crawl()
    # crawl.save_data()
    crawl.update()

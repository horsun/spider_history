import logging

from database import *
import requests
from lxml import html as lxml_html
import re


class ZJ_spider(object):
    def __init__(self):
        self.logger = logging.getLogger()

        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s [%(threadName)s][%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    def get_little_info(self):
        html = requests.get(url="https://www.zaojiu.com/zaojiu-talk").text
        max_page_xpath = "//nav[@class='pagination']/ul/li[6]/a/text()"
        doc = lxml_html.fromstring(html)
        max_page_list = doc.xpath(max_page_xpath)
        max_page = ''.join(max_page_list).strip()
        tk_info = TalkInfo()
        for page in range(int(max_page)):
            main_url = 'https://www.zaojiu.com/zaojiu-talk_{0}'.format(page + 1)
            html = requests.get(url=main_url).text
            doc = lxml_html.fromstring(html)
            url_xpath = "//div[@class='column is-half-mobile']/a/@href"
            post_time_xpath = "//div[@class='subtitle is-6 is-normal card-text']/text()"
            title_xpath = "//div[@class='title is-6 is-bold card-title has-clip is-2-lines']/text()"
            person_xpath = "//div[@class='title is-6 is-normal card-title card-speaker is-200']/text()"
            img_re = 'background-image:url\((.*?)\)'
            url_list = doc.xpath(url_xpath)
            post_time_list = doc.xpath(post_time_xpath)
            title_list = doc.xpath(title_xpath)
            person_list = doc.xpath(person_xpath)
            img_list = re.findall(img_re, html)
            for num, item in enumerate(url_list):
                speaker_info = person_list[num].split(' ')
                full_url = 'https://www.zaojiu.com' + item
                speaker = speaker_info[0]
                main_pic = img_list[num]
                title = title_list[num]
                post_time = post_time_list[num]
                try:
                    tk_info.create(
                        title=title,
                        speaker=speaker,
                        url=full_url,
                        post_time=post_time,
                        speaker_info=speaker_info,
                        main_pic=main_pic,
                    )
                except Exception as e:
                    self.logger.info("data has been saved ")

    def get_detail(self, item):
        tk_detail = TalkDetail()
        detail_url = item.url
        detail_id = item.id
        try:
            tk_detail.get(talkinfo_id=detail_id)
            print('item exist')

        except Exception as e:
            while True:
                try:
                    html = requests.get(url=detail_url).text
                    video_url = re.findall('<source src="(.*?)" type="video/mp4" />', html)
                    content = re.findall('<div class="content talk-content">(.*?)</div>', html)
                    tk_detail = TalkDetail()
                    tk_detail.create(
                        video_url=''.join(video_url).strip(),
                        content=''.join(content),
                        talkinfo_id=detail_id,
                    )
                    break
                except Exception as e:
                    pass


if __name__ == '__main__':
    spider = ZJ_spider()
    spider.get_little_info()
    talk_info = TalkInfo()
    all_item = talk_info.select()
    for item in all_item:
        spider.get_detail(item)

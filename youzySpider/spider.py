import logging
import re

import requests
from lxml import html as lxml_html

from database import *

from threading import Thread
from queue import Queue


class YouZySpider(object):
    def __int__(self):
        self.logger = logging.getLogger()

        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s [%(threadName)s][%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    def get_major_id(self, target_url):
        mj_g = MajorGenerality()
        html = requests.get(url=target_url).text
        doc = lxml_html.fromstring(html)
        main_title_xpath = "//div[@class='bk-major-list']/div/div[@class='major-title']/div/text()"
        main_title_list = doc.xpath(main_title_xpath)
        jobs_list = re.findall('data-content="(.*?)" ', html)
        count = 0
        print(jobs_list.__len__())
        for num, item in enumerate(main_title_list):
            second_title_xpath = "//div[@class='bk-major-list']/div[{0}]/div/a/text()".format(str(num + 1))
            second_title_list = doc.xpath(second_title_xpath)
            mj_g.create(name=item,
                        level='1')
            first_id = mj_g.get(name=item,
                                level='1').id
            for num_2, item_2 in enumerate(second_title_list):
                third_title_xpath = "//div[@class='bk-major-list']/div[{0}]/ul[{1}]/li/a".format(str(num + 1),
                                                                                                 str(num_2 + 1))
                third_title_list = doc.xpath(third_title_xpath + '/text()')
                third_url_list = doc.xpath(third_title_xpath + '/@href')
                mj_g.create(name=item_2,
                            level='2',
                            parent_id=first_id)
                second_id = mj_g.get(name=item_2,
                                     level='2').id
                for num_3, item_3 in enumerate(third_url_list):
                    major_name = third_title_list[num_3]
                    url_split_list = item_3.split('/')
                    major_id = url_split_list[-1]
                    sort_split = target_url.split('/')
                    sort = sort_split[-1]
                    job_recommend = jobs_list[count]
                    count += 1
                    mj_g.create(
                        name=major_name,
                        major_id=major_id,
                        job_recommend=job_recommend,
                        level='3',
                        parent_id=second_id,
                        sort=sort
                    )

    def get_detail(self, item):
        major_id = item.major_id
        Detail_url = 'https://www.youzy.cn/Majors/V3/Detail.aspx?majorId={0}&mc='.format(major_id)
        JobProspect_url = 'https://www.youzy.cn/Majors/V3/JobProspect.aspx?majorId={0}&mc='.format(major_id)
        html_detail = requests.get(url=Detail_url).text
        html_prospect = requests.get(url=JobProspect_url).text
        doc_detail = lxml_html.fromstring(html_detail)
        introduction_xpath = "//div[@class='introduce'][1]/div[@class='mt20'][1]/p[2]/text()"
        trainTarget_xpath = "//div[@class='introduce'][1]/div[@class='mt20'][2]/p[2]/text()"
        mainMajor_xpath = "//div[@class='introduce'][2]/div[@class='mt20'][1]/p[2]/text()"
        knowledgePower_xpath = "//div[@class='introduce'][2]/div[@class='mt20'][3]/p/text()"
        introduction = doc_detail.xpath(introduction_xpath)
        trainTarget = doc_detail.xpath(trainTarget_xpath)
        mainMajor = doc_detail.xpath(mainMajor_xpath)
        knowledgePower = doc_detail.xpath(knowledgePower_xpath)
        # 第二页
        doc_prospect = lxml_html.fromstring(html_prospect)
        jobTarget_xpath = "//div[@class='job-prospect']/div[@class='mt30']/p[2]/text()"
        job_re_1 = 'id="hdCities" />([\s\S]*)id="hdJobs" />'
        job_re = 'value="([\s\S]*)"'
        job_string_1 = re.findall(job_re_1, html_prospect)
        job_final_string = ''.join(job_string_1).strip()
        job_list = re.findall(job_re, job_final_string)
        cities_re_1 = 'id="hdSalaryYear" />([\s\S]*)id="hdCities" />'
        cities_re = 'value="([\s\S]*)"'
        cities_string_1 = re.findall(cities_re_1, html_prospect)
        cities_final_string = ''.join(cities_string_1).strip()
        cities_list = re.findall(cities_re, cities_final_string)
        jobTarget = doc_prospect.xpath(jobTarget_xpath)
        mj_detail = MajorDetail()
        mj_detail.create(
            generality_id=item.id,
            introduction=''.join(introduction).strip(),
            trainTarget=''.join(trainTarget).strip(),
            mainMajor=''.join(mainMajor).strip(),
            knowledgePower=''.join(knowledgePower).strip(),
            jobTarget=''.join(jobTarget).strip(),
            jobZoom=''.join(cities_list).strip(),
            jobList=''.join(job_list).strip(),
        )


if __name__ == '__main__':
    spider = YouZySpider()
    url = [
        'https://www.youzy.cn/major/index/bk',
        'https://www.youzy.cn/major/index/zk',
    ]
    for item in url:
        spider.get_major_id(target_url=item)

    mj = MajorGenerality()
    mj_all = mj.select().where(MajorGenerality.level == '3')
    thread_num = 5
    q = Queue()

    for item in mj_all:
        q.put(item)


    def run():
        while True:
            item = q.get()
            spider.get_detail(item)
            q.task_done()


    for i in range(thread_num):
        t = Thread(target=run)
        t.setDaemon(True)
        t.start()
    q.join()

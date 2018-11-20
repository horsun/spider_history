import logging
import re
import time
from datetime import datetime
from queue import Queue
from threading import Thread

import requests
from bs4 import BeautifulSoup
from lxml import html as lxml_html

from database import *
from lib.config import Config


class ZLSpider(object):
    def __init__(self):
        self.logger = logging.getLogger()

        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s [%(threadName)s][%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
        SpiderConfig = Config.SpiderConfig
        self.headers = SpiderConfig.headers.json()
        self.errorLogFileName = 'errorLog.txt'

    def get_url(self):
        html = requests.get(url='https://cimg.zhaopin.cn/PCIndex2018/js/MajorMap.js', headers=self.headers)
        html.encoding = 'utf-8'
        html = html.text
        list_2 = html.split(';')
        string_1 = list_2[0]
        string = re.findall("var MajorMap = ([\s\S]*)", string_1)
        id = re.findall('"Id": "(.*?)"', string[0])
        name = re.findall('"Name": "(.*?)"', string[0])
        JobSubCategory = re.findall('"JobSubCategory": "(.*?)"', string[0])
        dist = {

        }
        for i in range(len(id)):

            dist[i] = {}
            dist[i]['Id'] = id[i]
            dist[i]['name'] = name[i]
            dist[i]['url'] = 'https://xiaoyuan.zhaopin.com/full/jobs/' + JobSubCategory[i]
            try:
                Major.get(url=dist[i]['url'], name=dist[i]['name'])
                self.logger.info('该url已经爬过了:' + dist[i]['name'])
                continue
            except Exception as e:
                pass
            while True:
                try:
                    html = requests.get(url=dist[i]['url'], headers=self.headers).text
                    doc = lxml_html.fromstring(html)
                    pages = doc.xpath("//div/span[@class='searchResultPagePer fr']/text()")
                    print(pages)
                    page_1 = pages[0]
                    page_2 = page_1.split('/')
                    dist[i]['pages'] = page_2[1]
                    mj = Major()
                    mj.create(name=name[i],
                              pages=dist[i]['pages'],
                              url='https://xiaoyuan.zhaopin.com/full/jobs/' + JobSubCategory[i], )
                    break
                except:
                    pass

    def get_detail(self, item):
        pages = item.pages
        url_pg = item.url
        parent_id = item.id
        for i in range(int(pages)):
            page_str = '/0_0_0_0_-1_0_{0}_0'.format(i + 1)
            full_page_url = url_pg + page_str
            try:
                html = requests.get(url=full_page_url,
                                    headers=self.headers,
                                    ).text
                soup = BeautifulSoup(html, 'lxml')
                doc = lxml_html.fromstring(html)
                xpath_descrip = "//li/div/p[@class='searchResultJobdescription']/span/text()"
                description_list = doc.xpath(xpath_descrip)
                time.sleep(3)
                jobName = []
                url = []
                companyName = []
                cityName = []
                hireNumber = []
                companyIndustry = []
                regex = "__ga__fullResult(.*)postname_clicksfullresult(.*)postnames_001"
                posts = soup.findAll("a", {"class": re.compile(regex)})
                for post in posts[::2]:
                    title = post.get_text()
                    title_url = post.get('href')
                    jobName.append(title)
                    url.append(title_url)

                facts = soup.findAll("p", {"class": "searchResultCompanyname"})
                for fact in facts[::2]:
                    cp_name = fact.get_text()
                    companyName.append(cp_name)

                cities = soup.findAll("em", {"class": "searchResultJobCityval"})
                for city in cities[::2]:
                    city_name = city.get_text()
                    cityName.append(city_name)

                nums = soup.findAll("em", {"class": "searchResultJobPeopnum"})
                for num in nums:
                    h_number = num.get_text()
                    hireNumber.append(h_number)  # hireNumber

                labs = soup.findAll("p", {"class": "searchResultCompanyIndustry"})
                for lab in labs:
                    cp_industry = lab.get_text()
                    companyIndustry.append(cp_industry)  # companyIndustry
                time_regex = 'datecreated="(.*?)"'
                times = re.findall(time_regex, html)
                jobType = '<span>职位类别：<em>(.*?)</em></span>'
                jobTypes = re.findall(jobType, html)
                for no, item in enumerate(jobName):
                    mj_detail = MajorDetail()
                    mj_detail.create(
                        major_id=parent_id,
                        jobName=jobName[no],
                        companyName=companyName[no],
                        url=url[no],
                        description=description_list[no],
                        cityName=cityName[no],
                        companyIndustry=companyIndustry[no],
                        jobType=jobTypes[no],
                        hireNumber=hireNumber[no],
                        postTime=times[no],
                    )
            except Exception as e:
                logging.warning('error:' + e.__repr__() + 'url:' + full_page_url)
                newfile = open(self.errorLogFileName, 'a')
                newfile.write('error:' + e.__repr__() + 'url:' + full_page_url + str(datetime.now()))
                newfile.write('\n')
                newfile.close()


print('tt')

if __name__ == '__main__':
    spider = ZLSpider()
    spider.get_url()
    q = Queue()
    Thread_num = 5

    start_time = datetime.now()
    print(start_time)

    for no, item in enumerate(Major.select()):
        q.put(item)


    def run():
        while True:
            item = q.get()
            spider.get_detail(item=item)
            q.task_done()


    for i in range(Thread_num):
        t = Thread(target=run)
        t.setDaemon(True)
        t.start()
    q.join()
    end_time = datetime.now()
    take_time = end_time - start_time
    print(end_time)
    print("用了多久", take_time)

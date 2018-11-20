import json
import random
import time
from lxml import html as lxml_html
import requests
import re
from database import *


class XZ_Occupation(object):
    # 职业百科
    def __int__(self):
        pass

    def run_spider(self):
        total_html = requests.get(url='http://xz.chsi.com.cn/ajax/occuindexqt.action').text
        html_json = json.loads(total_html)
        for no, content in enumerate(html_json):
            ktid = content['ktid']
            ktname = content['ktname']
            children = content['occInfos']
            mj_little = Occupation()
            try:
                mj_little.create(
                    kt_id=ktid,
                    name=ktname,
                    level='1',
                )
            except Exception as e:
                print(ktname + '已经有了')
            parent_id = mj_little.get(kt_id=ktid).id
            if children.__len__() != 0:
                for no_2, content_2 in enumerate(children):
                    detail_url = 'http://xz.chsi.com.cn/ajax/occudetail.action' + '?id=' + content_2['id']
                    html = requests.post(url=detail_url).text
                    print(html)

                    try:
                        mj_little.create(
                            parent_id=parent_id,
                            url_id='http://xz.chsi.com.cn/occupation/occudetail.action?id=' + content_2['id'],
                            xl_id=content_2['xlid'],
                            name=content_2['name'],
                            detail=html,
                            level='2'
                        )
                        sec = random.randint(4, 9)
                        time.sleep(sec)
                        print(sec)
                    except Exception as e:
                        print(content_2['name'] + '已经有了')
            else:
                continue


class XZ_Speciality(object):
    # 专业百科
    def __int__(self):
        pass

    def run_spider(self):
        html = requests.get(url='http://xz.chsi.com.cn/speciality/list.action?start=0').text
        doc = lxml_html.fromstring(html)
        page_list = doc.xpath("//li[@class='lip able'][5]/text()")
        total_page = int(page_list[0])
        count = 0
        for i in range(total_page):
            url_tail = 'start=' + str(i * 15)
            request_url = 'http://xz.chsi.com.cn/speciality/list.action?' + url_tail
            html = requests.get(url=request_url).text
            doc = lxml_html.fromstring(html)
            star_value_re = '<span class="gold" data-value="(.*?)">'
            star_list = re.findall(star_value_re, html)
            url_re = "<td><a href='(.*?)' targe"
            url_list = re.findall(url_re, html)
            major_name_re = 'target="_blank">(.*?)</a></td>'
            major_name_list = re.findall(major_name_re, html)
            edu_level_xpath = "//table/tbody/tr/td[3]/text()"
            edu_level_list = doc.xpath(edu_level_xpath)
            kind_xpath = '//table/tbody/tr/td[4]/text()'
            kind_list = doc.xpath(kind_xpath)
            course_xpath = '//table/tbody/tr/td[5]/text()'
            course_list = doc.xpath(course_xpath)
            for num, url in enumerate(url_list):
                mj = Major()
                full_url = 'http://xz.chsi.com.cn' + url
                html_text = requests.get(url=full_url).text
                try:
                    mj.create(
                        major_name=major_name_list[num],
                        star_value=star_list[num],
                        edu_level=edu_level_list[num],
                        kind=kind_list[num],
                        course=course_list[num],
                        detail=html_text.strip(),
                        url=full_url)
                    count += 1
                except Exception as e:
                    print(e.__repr__())
        print(count)


if __name__ == '__main__':
    spider_occudetail = XZ_Occupation()
    spider_occudetail.run_spider()
    spider_speciality = XZ_Speciality()
    spider_speciality.run_spider()

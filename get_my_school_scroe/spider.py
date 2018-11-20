import requests
from PIL import Image
import re
from lxml import html as lxml_html


class ScoreSpider(object):
    def __init__(self):
        self.url1 = 'http://jwxt.zwu.edu.cn/CheckCode.aspx'  # 验证码的地址
        self.url2 = 'http://jwxt.zwu.edu.cn/default2.aspx'  # 登陆网站 获取session
        # 成绩页面第一次访问 主要用以获取 __VIEWSTATE 等参数  成绩获取request
        self.url4 = 'http://jwxt.zwu.edu.cn/xscj_gc.aspx?xh={0}&xm=%BD%F0%BA%C6&gnmkdm=N121605'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        }
        self.headers2 = {
            'Host': 'jwxt.zwu.edu.cn',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0(Windows NT 10.0;Win64;x64)AppleWebKit /537.36(KHTML, like Gecko)Chrome / 67.0.3396.62 Safari / 537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'http://jwxt.zwu.edu.cn/xs_main.aspx?xh=2014014701',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh,en;q=0.9,zh-CN;q=0.8',

        }
        self.score_headers = {
            'Host': 'jwxt.zwu.edu.cn',
            'Connection': 'keep-alive',
            'Content-Length': '2243',
            'Cache-Control': 'max-age=0',
            'Origin': 'http://jwxt.zwu.edu.cn',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'http://jwxt.zwu.edu.cn/xscj_gc.aspx?xh=2014014701&xm=%BD%F0%BA%C6&gnmkdm=N121605',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh,en;q=0.9,zh-CN;q=0.8',

        }
        self.student_id = '**********'
        self.pwd = '**********'
        self.session = requests.session()
        self.get_code_pic()
        self.get_session_by_data()
        self.get_response_data()

    def get_code_pic(self):
        """
        获取验证码图片并展示
        :return:
        """
        html = self.session.get(self.url1, headers=self.headers).content
        picture_file = open('code.jpg', 'wb')
        picture_file.write(html)
        picture_file.close()
        self.img = Image.open('code.jpg')
        self.img.show()

    def get_session_by_data(self):
        """
        通过requests.session().get()登陆网站获取cookies
        :return:
        """
        data = {}
        data['__VIEWSTATE'] = 'dDwxOTE1OTY0NjYyOzs+MZrC56cZEob9TNcWW3i0g/UC7qg='
        data['__VIEWSTATEGENERATOR'] = '92719903'
        data['TextBox1'] = self.student_id
        data['TextBox2'] = self.pwd
        data['TextBox3'] = input('请输入验证码')
        data['RadioButtonList1'] = '%D1%A7%C9%FA'
        data['Button1'] = ''
        self.ask_request = self.session.post(url=self.url2, data=data, headers=self.headers)

    def get_response_data(self):
        """
        通过第一次访问 self.url4 来获取 第二次访问 self.url的的所需参数
        第一次 访问self.url4 是get方法
        第二次 访问self.url4 是post方法 post带了写 data 所需参数 需要从第一次访问所返回的html中找到
        (第一次是get方法 请求返回后 html 内有__VIEWSTATE 和__VIEWSTATEGENERATOR 俩大参数)
        :return:
        """
        response = self.session.get(url=self.url4.format(self.student_id),
                                    headers=self.headers2,
                                    )
        response.encoding = 'gb2312'
        html = response.text
        __VIEWSTATE = re.findall('name="__VIEWSTATE" value="(.*?)"', html)
        __VIEWSTATEGENERATOR = re.findall('name="__VIEWSTATEGENERATOR" value="(.*?)"', html)
        self.data = {
            '__VIEWSTATE': ''.join(__VIEWSTATE),
            '__VIEWSTATEGENERATOR': ''.join(__VIEWSTATEGENERATOR),
            'ddlXN': '',
            'ddlXQ': '',
            'Button1': '%B0%B4%D1%A7%C6%DA%B2%E9%D1%AF', }

    def get_score(self):
        """
        获取目标url的html内容
        接下来就可以对目标页面进行解析
        可以通过正则或者xpath来提取数据
        :return:
        """
        cookies = self.session.cookies
        response = self.session.post(url=self.url4.format(self.student_id),
                                     data=self.data,
                                     headers=self.score_headers,
                                     cookies=cookies
                                     )
        response.encoding = 'gb2312'
        html = response.text
        print(html)
        doc = lxml_html.fromstring(html)


if __name__ == '__main__':
    ss = ScoreSpider()
    ss.get_score()

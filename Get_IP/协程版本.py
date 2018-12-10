import time

import lxml.html
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
}


class ProxyCrawl(object):
    def __init__(self, url):
        self.url = url
        self.get_ip()
        self.success = []

    def get_ip(self):
        html = requests.get(self.url, headers=headers).text
        time.sleep(5)
        doc = lxml.html.fromstring(html)
        ip = doc.xpath('//td[2]/text()')
        port = doc.xpath('//td[3]/text()')
        head = doc.xpath('//td[6]/text()')
        for i in range(0, len(ip)):
            each = '{}'.format(head[i]) + '://' + ip[i] + ':' + port[i]
            yield {
                'http': each,
                'https': each,
            }

    def test_ip(self):
        # 通过yield 使方法变成一个消费者
        while True:
            proxy = yield
            try:
                requests.get(url='http://www.baidu.com', proxies=proxy, timeout=2)
            except:
                print('both model all failed _________', proxy)
            else:
                print('success ip:', proxy)
                self.success.append(proxy)

    def save_ip(self):
        #----主要协程用法----
        tset_iiip = self.test_ip()
        next(tset_iiip)
        for item in self.get_ip():
            tset_iiip.send(item)
        tset_iiip.close()
        #------------------
        with open('ipipmuti.txt', 'a') as newfile:
            for proxies in self.success:
                newfile.write(str(proxies))
                newfile.write('\n')
                print('save success')


def main(page):
    # page = yield
    url = 'http://www.xicidaili.com/nn/{}'.format(page)
    spider = ProxyCrawl(url)
    spider.save_ip()


if __name__ == '__main__':
    start = time.time()
    for page in range(1, 3):
        main(page)
    # 协程 233.32704663276672
    end = time.time()
    used = end - start
    print(used)

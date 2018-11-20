import requests
import lxml.html
import time

from requests.exceptions import ConnectTimeout
from urllib3 import HTTPSConnectionPool
from urllib3.exceptions import MaxRetryError

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
}


class ProxyCrawl(object):
    def __init__(self, url):
        self.url = url
        self.get_ip()

    def get_ip(self):
        html = requests.get(self.url, headers=headers).text
        time.sleep(5)
        doc = lxml.html.fromstring(html)
        ip = doc.xpath('//td[2]/text()')
        port = doc.xpath('//td[3]/text()')
        head = doc.xpath('//td[6]/text()')
        self.proxies = []
        for i in range(0, len(ip)):
            each = '{}'.format(head[i]) + '://' + ip[i] + ':' + port[i]
            self.proxies.append({
                'http': each,
                'https': each,
            })
        self.test_ip()
        self.save_ip()

    def test_ip(self):
        self.proxy_yes = []
        for proxy in self.proxies:
            try:
                requests.get(url='http://118.25.126.182/', proxies=proxy, timeout=2)
            except (MaxRetryError, ConnectTimeout, HTTPSConnectionPool):
                print('both model all failed _________', proxy)
            else:
                print('success ip:', proxy)
                self.proxy_yes.append(proxy)

    def save_ip(self):
        with open('ipipmuti.txt', 'a') as newfile:
            for proxies in self.proxy_yes:
                newfile.write(str(proxies))
                newfile.write('\n')
                print('save success')


def main(page):
    url = 'http://www.xicidaili.com/nn/{}'.format(page)
    spider = ProxyCrawl(url)
    spider.get_ip()


if __name__ == '__main__':
    start = time.time()
    # /---------------------------
    # 普通io阻塞
    # for page in range(1, 3):
    #     main(page)
    #
    # take 242.97173595428467 s
    # /---------------------------

    # /---------------------------
    # 线程池
    # from multiprocessing import Pool
    # pool = Pool()
    # pool.map(main, [page for page in range(1, 3)])
    #
    # take 150.44547533988953 s
    # /---------------------------

    # /---------------------------
    # 多线程
    from queue import Queue
    from threading import Thread

    q = Queue()
    thread_num = 5
    for page in range(1, 6):
        q.put(page)


    def run():
        while True:
            item = q.get()
            main(item)
            q.task_done()


    for i in range(thread_num):
        t = Thread(target=run)
        t.setDaemon(True)
        t.start()
    q.join()
    # take 147.5603437423706s
    # /---------------------------

    # /---------------------------
    # 异步实现
    # /---------------------------
    end = time.time()
    used = end - start
    print(used)

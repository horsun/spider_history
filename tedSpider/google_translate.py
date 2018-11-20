import execjs

from lib.proxy import *


class GGTranslate(object):
    def __init__(self):
        SpiderConfig = Config.SpiderConfig
        self.headers = SpiderConfig.headers.json()
        self.logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s [%(threadName)s][%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
        self.ctx = execjs.compile(""" 
        function TL(a) { 
        var k = ""; 
        var b = 406644; 
        var b1 = 3293161072; 

        var jd = "."; 
        var $b = "+-a^+6"; 
        var Zb = "+-3^+b+-f"; 

        for (var e = [], f = 0, g = 0; g < a.length; g++) { 
            var m = a.charCodeAt(g); 
            128 > m ? e[f++] = m : (2048 > m ? e[f++] = m >> 6 | 192 : (55296 == (m & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (m = 65536 + ((m & 1023) << 10) + (a.charCodeAt(++g) & 1023), 
            e[f++] = m >> 18 | 240, 
            e[f++] = m >> 12 & 63 | 128) : e[f++] = m >> 12 | 224, 
            e[f++] = m >> 6 & 63 | 128), 
            e[f++] = m & 63 | 128) 
        } 
        a = b; 
        for (f = 0; f < e.length; f++) a += e[f], 
        a = RL(a, $b); 
        a = RL(a, Zb); 
        a ^= b1 || 0; 
        0 > a && (a = (a & 2147483647) + 2147483648); 
        a %= 1E6; 
        return a.toString() + jd + (a ^ b) 
    }; 

    function RL(a, b) { 
        var t = "a"; 
        var Yb = "+"; 
        for (var c = 0; c < b.length - 2; c += 3) { 
            var d = b.charAt(c + 2), 
            d = d >= t ? d.charCodeAt(0) - 87 : Number(d), 
            d = b.charAt(c + 1) == Yb ? a >>> d: a << d; 
            a = b.charAt(c) == Yb ? a + d & 4294967295 : a ^ d 
        } 
        return a 
    } 
    """)

    def getTk(self, text):
        return self.ctx.call("TL", text)

    def getProxy(self):
        proxy = ScyllaProxy().getProxy()
        print(proxy)
        return {'https': proxy}

    def translate(self, content):
        tk = self.getTk(content)
        if len(content) > 4891:
            print("翻译的长度超过限制！！！")
            return

        param = {'tk': tk, 'q': content}
        while True:
            try:
                proxies = self.getProxy()
                result = requests.get("""https://translate.google.cn/translate_a/single?client=t&sl=en 
                                &tl=zh-CN&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss 
                                &dt=t&ie=UTF-8&oe=UTF-8&clearbtn=1&otf=1&pc=1&srcrom=0&ssel=0&tsel=0&kc=2""",
                                      params=param,
                                      proxies=proxies,
                                      timeout=10,
                                      )

                # 返回的结果为Json，解析为一个嵌套列表
                js_list = result.json()
                trans_result = js_list[0][0][0]
                print(trans_result)
                break
            except Exception as e:
                print(e.__repr__())

        return trans_result


if __name__ == "__main__":
    ts = GGTranslate()
    chinese = ts.translate('你好')
    print(chinese)
